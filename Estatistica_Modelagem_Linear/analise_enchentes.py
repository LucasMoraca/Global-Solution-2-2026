# -*- coding: utf-8 -*-
"""
GLOBAL SOLUTION 2026.2 - CitizenTech | Modelagem Linear para Aprendizado de Máquina
Projeto: Plantão Enchente (Citizen Assist AI)

Integrantes:
  Gabriel Barbosa Furin ............ RM 572941
  Lucas Kiodi Moraca ............... RM 571004
  Renan Fracalossi Mano da Silva ... RM 569610

Base de dados (REAL, do Brasil, não sintética):
  enchentes_brasil_uf_ano_2013_2025.csv - painel de 27 UFs x 13 anos (351 linhas) com a
  contagem de registros oficiais de desastres e os danos das enchentes.
  Fonte: Atlas Digital de Desastres no Brasil (Sedec/MIDR), originado no S2iD, versão
  consolidada v1.1 (06/08/2026). Enchente = Alagamentos + Enxurradas + Inundações.
  Como a base foi montada: ver preparar_base.py.

Como executar (o CSV deve estar na mesma pasta deste arquivo):
  pip install numpy pandas scipy statsmodels scikit-learn matplotlib seaborn
  python analise_enchentes.py

Saídas: tabelas no terminal, figuras em ./figuras/ e resultados.json.
Resolve os itens 02 a 06 do enunciado; o item 07 (relatório) usa estes resultados.

Observação de método: as contagens e os danos são muito assimétricos; por isso as variáveis
são analisadas na escala  L(x) = log10(1 + x). O "+1" mantém os estados-ano sem registro (0).
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold
from statsmodels.stats.outliers_influence import variance_inflation_factor

PASTA = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(PASTA, "figuras")
os.makedirs(FIG, exist_ok=True)
SEMENTE = 2026            # reprodutibilidade das amostras (item 03) e da validação cruzada
R = {}                    # todos os resultados (vai para resultados.json)

sns.set_theme(style="whitegrid", context="notebook")
AZUL, LARANJA, VERMELHO, CINZA = "#1f5fa8", "#e8871e", "#c0392b", "#6b7280"


def L(x):
    """Escala log10(1 + x)."""
    return np.log10(1 + x)


def de_volta(v):
    """Volta da escala log10(1 + x) para a unidade original."""
    return 10 ** v - 1


def titulo(txt):
    print("\n" + "=" * 78 + f"\n{txt}\n" + "=" * 78)


def salvar(nome):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, nome), dpi=170)
    plt.close()


# ----------------------------------------------------------------------------
# 01) Carga e exploração da base
# ----------------------------------------------------------------------------
titulo("01) BASE DE DADOS")
df = pd.read_csv(os.path.join(PASTA, "enchentes_brasil_uf_ano_2013_2025.csv"))
# variáveis na escala log10(1+x)
df["E"] = L(df["registros_enchentes"])          # registros de enchente
df["C"] = L(df["chuvas_intensas"])              # registros de chuvas intensas
df["M"] = L(df["movimento_massa"])              # registros de movimento de massa
df["V"] = L(df["vendavais_ciclones"])           # registros de vendavais e ciclones
df["S"] = L(df["estiagem_seca"])                # registros de estiagem e seca
df["D"] = L(df["desabrigados_enchentes"])       # desabrigados por enchentes
df["Dl"] = L(df["desalojados_enchentes"])       # desalojados por enchentes
df["OBITO"] = (df["mortos_enchentes"] > 0).astype(int)

R["base"] = {
    "n_linhas": int(len(df)), "n_ufs": int(df.uf.nunique()),
    "ano_inicial": int(df.ano.min()), "ano_final": int(df.ano.max()),
    "valores_faltantes": int(df.isna().sum().sum()),
    "registros_enchentes_total": int(df.registros_enchentes.sum()),
    "mortos_total": int(df.mortos_enchentes.sum()),
    "pessoas_afetadas_total": int(df.pessoas_afetadas_enchentes.sum()),
    "desabrigados_total": int(df.desabrigados_enchentes.sum()),
    "desalojados_total": int(df.desalojados_enchentes.sum()),
    "prejuizo_total_rs": float(df.prejuizo_enchentes_rs.sum()),
    "uf_ano_sem_enchente": int((df.registros_enchentes == 0).sum()),
    "uf_ano_com_obito": int(df.OBITO.sum()),
    "prevalencia_obito": float(df.OBITO.mean()),
    # coerência interna: alagamentos + enxurradas + inundações = registros de enchente
    "max_dif_tipologias": int((df.alagamentos + df.enxurradas + df.inundacoes - df.registros_enchentes).abs().max()),
}
print(R["base"])
cols_desc = ["registros_enchentes", "chuvas_intensas", "movimento_massa", "vendavais_ciclones",
             "estiagem_seca", "desabrigados_enchentes", "desalojados_enchentes", "mortos_enchentes"]
print(df[cols_desc].describe().round(1).T)
R["descritiva_original"] = df[cols_desc].agg(["mean", "median", "std", "min", "max"]).round(1).to_dict()
R["assimetria_original_vs_log"] = {
    c: [float(df[c].skew()), float(L(df[c]).skew())] for c in cols_desc[:7]}

por_regiao = df.groupby("regiao")["registros_enchentes"].agg(["sum", "mean"]).round(1)
por_uf = df.groupby("uf")["registros_enchentes"].sum().sort_values(ascending=False)
por_ano = df.groupby("ano")["registros_enchentes"].sum()
R["por_regiao"] = por_regiao.to_dict("index")
R["top_ufs"] = por_uf.head(5).to_dict()
R["por_ano"] = {int(k): int(v) for k, v in por_ano.items()}
print(por_regiao)
print(por_uf.head(5))

# Figura 1 - panorama: registros por ano e por região
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.5, 1]})
axs[0].bar(por_ano.index, por_ano.values, color=AZUL)
axs[0].set(title="Registros de enchente por ano (Brasil)", xlabel="Ano", ylabel="Registros")
reg = por_regiao["sum"].sort_values()
axs[1].barh(reg.index, reg.values, color=LARANJA)
axs[1].set(title="Registros por região, 2013-2025", xlabel="Registros")
salvar("fig1_panorama.png")

# ----------------------------------------------------------------------------
# 02) Distribuição Normal - variável: E = log10(1 + registros de enchente por UF-ano)
#     nos estados-ano com pelo menos 1 registro de enchente ("intensidade quando ocorre")
# ----------------------------------------------------------------------------
titulo("02) PROBABILIDADES (DISTRIBUIÇÃO NORMAL) - REGISTROS DE ENCHENTE")
x = df.loc[df["registros_enchentes"] > 0, "E"]   # exclui os estados-ano sem enchente (zeros)
mu, sigma = x.mean(), x.std(ddof=0)       # estas observações são tratadas como a população
mediana = x.median()
sw = stats.shapiro(x)
p_a = stats.norm.cdf(mu, mu, sigma)
p_b = 1 - stats.norm.cdf(mediana, mu, sigma)


def classificar(p):
    """Escala usada neste trabalho para classificar o resultado probabilístico."""
    if p < 0.10:
        return "muito improvável"
    if p < 0.40:
        return "improvável"
    if p <= 0.60:
        return "equiprovável (chance semelhante à do evento contrário)"
    if p <= 0.90:
        return "provável"
    return "muito provável"


R["q02"] = {
    "variavel": "E = log10(1 + registros de enchente por UF-ano), UF-ano com >= 1 registro",
    "n": int(len(x)),
    "media": float(mu), "desvio_padrao_pop": float(sigma), "mediana": float(mediana),
    "assimetria": float(x.skew()), "shapiro_W": float(sw.statistic), "shapiro_p": float(sw.pvalue),
    "media_em_registros": float(de_volta(mu)), "mediana_em_registros": float(de_volta(mediana)),
    "p_menor_que_media": float(p_a), "classe_a": classificar(p_a),
    "p_maior_que_mediana": float(p_b), "classe_b": classificar(p_b),
    "z_mediana": float((mediana - mu) / sigma),
}
print(f"média = {mu:.4f} | desvio padrão (pop.) = {sigma:.4f} | mediana = {mediana:.4f} | assimetria = {x.skew():.3f}")
print(f"(em registros: média geométrica ~ {de_volta(mu):.1f}; mediana = {de_volta(mediana):.1f})")
print(f"Shapiro-Wilk: W = {sw.statistic:.4f}, p = {sw.pvalue:.4f}")
print(f"a) P(X < média)   = {p_a:.4f} -> {classificar(p_a)}")
print(f"b) P(X > mediana) = {p_b:.4f} -> {classificar(p_b)}")

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(x, bins=16, density=True, color=AZUL, alpha=0.55, edgecolor="white", label=f"Dados ({len(x)} UF-ano com enchente)")
xs = np.linspace(x.min() - 0.3, x.max() + 0.3, 400)
ax.plot(xs, stats.norm.pdf(xs, mu, sigma), color=LARANJA, lw=2.2, label="Normal ajustada")
ax.axvline(mu, color="black", ls="--", lw=1.2, label=f"Média = {mu:.2f}")
ax.axvline(mediana, color=VERMELHO, ls=":", lw=1.8, label=f"Mediana = {mediana:.2f}")
ax.set(title="Registros de enchente por UF-ano: histograma e Normal ajustada",
       xlabel="E = log10(1 + registros de enchente)", ylabel="Densidade")
ax.legend(fontsize=8)
salvar("fig2_normal.png")

# ----------------------------------------------------------------------------
# 03) Teste de hipótese para a média (teste Z; sigma = desvio padrão populacional dos dados)
# ----------------------------------------------------------------------------
titulo("03) TESTES DE HIPÓTESE PARA A MÉDIA (Z)")
rng = np.random.default_rng(SEMENTE)
mu0 = mu


def teste_z(n, alfa, cauda):
    amostra = rng.choice(x.to_numpy(), size=n, replace=False)
    xbar = amostra.mean()
    z = (xbar - mu0) / (sigma / np.sqrt(n))
    if cauda == "menor":
        zc, p = stats.norm.ppf(alfa), stats.norm.cdf(z)
        rejeita = z < zc
    else:
        zc, p = stats.norm.ppf(1 - alfa), 1 - stats.norm.cdf(z)
        rejeita = z > zc
    return {"n": n, "alfa": alfa, "H0": f"mu = {mu0:.4f}",
            "H1": f"mu {'<' if cauda == 'menor' else '>'} {mu0:.4f}",
            "media_amostral": float(xbar), "erro_padrao": float(sigma / np.sqrt(n)),
            "z_calculado": float(z), "z_critico": float(zc), "p_valor": float(p),
            "decisao": "Rejeita H0" if rejeita else "Não rejeita H0"}


R["q03a"] = teste_z(20, 0.06, "menor")
R["q03b"] = teste_z(25, 0.09, "maior")
for k in ("q03a", "q03b"):
    r = R[k]
    print(f"{k[-1]}) n={r['n']}, alfa={r['alfa']:.0%}, H1: {r['H1']} | média amostral={r['media_amostral']:.4f} "
          f"| Z={r['z_calculado']:.3f} | Zcrit={r['z_critico']:.3f} | p={r['p_valor']:.4f} -> {r['decisao']}")

fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
zs = np.linspace(-4, 4, 400)
for ax, k, cauda in zip(axs, ("q03a", "q03b"), ("menor", "maior")):
    r = R[k]
    ax.plot(zs, stats.norm.pdf(zs), color="black")
    mask = zs <= r["z_critico"] if cauda == "menor" else zs >= r["z_critico"]
    ax.fill_between(zs, stats.norm.pdf(zs), where=mask, color=VERMELHO, alpha=0.4, label="Região de rejeição")
    ax.axvline(r["z_calculado"], color=AZUL, lw=2, label=f"Z calculado = {r['z_calculado']:.2f}")
    ax.set(title=f"Teste {k[-1]}) n={r['n']}, α={r['alfa']:.0%}, H1: μ {'<' if cauda == 'menor' else '>'} μ0",
           xlabel="Z", ylabel="Densidade")
    ax.legend(fontsize=8)
salvar("fig3_testes_z.png")

# ----------------------------------------------------------------------------
# 04) Análise bivariada: E (registros de enchente) em função de C (chuvas intensas)
# ----------------------------------------------------------------------------
titulo("04) ANÁLISE BIVARIADA - ENCHENTES x CHUVAS INTENSAS")
X1, Y1 = df["C"], df["E"]
cov = np.cov(X1, Y1, ddof=1)[0, 1]
pr = stats.pearsonr(X1, Y1)
mod1 = sm.OLS(Y1, sm.add_constant(X1)).fit()
b0, b1 = mod1.params["const"], mod1.params["C"]
chuvas_prev = 20                                   # 20 registros de chuvas intensas no estado-ano
x_prev = float(L(chuvas_prev))
pred1 = mod1.get_prediction(np.array([[1.0, x_prev]])).summary_frame(alpha=0.05)
y_prev = float(pred1["mean"].iloc[0])

R["q04"] = {
    "covariancia": float(cov), "pearson_r": float(pr.statistic), "pearson_p": float(pr.pvalue),
    "intercepto": float(b0), "inclinacao": float(b1), "p_inclinacao": float(mod1.pvalues["C"]),
    "ic95_inclinacao": [float(v) for v in mod1.conf_int().loc["C"]],
    "r2": float(mod1.rsquared), "r2_ajustado": float(mod1.rsquared_adj),
    "F": float(mod1.fvalue), "F_p": float(mod1.f_pvalue), "gl": [int(mod1.df_model), int(mod1.df_resid)],
    "erro_padrao_residual": float(np.sqrt(mod1.scale)),
    "previsao_chuvas": chuvas_prev, "previsao_E": y_prev, "previsao_registros": float(de_volta(y_prev)),
    "ip95_E": [float(pred1["obs_ci_lower"].iloc[0]), float(pred1["obs_ci_upper"].iloc[0])],
    "ip95_registros": [float(de_volta(pred1["obs_ci_lower"].iloc[0])), float(de_volta(pred1["obs_ci_upper"].iloc[0]))],
    "fator_por_dobro": float(2 ** b1),
}
print(f"Covariância = {cov:.4f} | Pearson r = {pr.statistic:.4f} (p = {pr.pvalue:.2e})")
print(f"Equação: E = {b0:.4f} + {b1:.4f} x C")
print(f"R² = {mod1.rsquared:.4f} | R² aj. = {mod1.rsquared_adj:.4f} | F({int(mod1.df_model)},{int(mod1.df_resid)}) = {mod1.fvalue:.2f} (p = {mod1.f_pvalue:.2e})")
print(f"Previsão: {chuvas_prev} registros de chuvas intensas -> E = {y_prev:.3f} = {de_volta(y_prev):.1f} registros de enchente "
      f"(IP95%: {R['q04']['ip95_registros'][0]:.1f} a {R['q04']['ip95_registros'][1]:.1f})")
print(f"Dobrar os registros de chuvas intensas multiplica os de enchente por ~{2 ** b1:.2f}")

fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.scatter(X1, Y1, s=26, color=AZUL, alpha=0.6, edgecolor="white", label="UF-ano")
xx = np.linspace(X1.min(), X1.max(), 100)
ax.plot(xx, b0 + b1 * xx, color=VERMELHO, lw=2.2, label=f"Reta: E = {b0:.2f} + {b1:.2f}·C  (R² = {mod1.rsquared:.2f})")
ax.set(title="Dispersão: chuvas intensas x enchentes (27 UFs, 2013-2025)",
       xlabel="C = log10(1 + registros de chuvas intensas)", ylabel="E = log10(1 + registros de enchente)")
ax.legend(fontsize=8)
salvar("fig4_dispersao_reta.png")

fig, ax = plt.subplots(figsize=(4.8, 3.9))
sns.heatmap(df[["C", "E"]].corr(), annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1,
            square=True, cbar_kws={"label": "r de Pearson"}, ax=ax)
ax.set_title("Correlação de Pearson: C x E")
salvar("fig5_correlacao_bivariada.png")

# ----------------------------------------------------------------------------
# 05) Regressão linear múltipla: E ~ C + M + V + S
# ----------------------------------------------------------------------------
titulo("05) REGRESSÃO LINEAR MÚLTIPLA")
VARS = ["C", "M", "V", "S"]
dados5 = df[["E"] + VARS]
cov_m, cor_m = dados5.cov(), dados5.corr()
Xm = sm.add_constant(df[VARS])
mod5 = sm.OLS(df["E"], Xm).fit()
vif = {v: float(variance_inflation_factor(Xm.values, i)) for i, v in enumerate(Xm.columns) if v != "const"}
res_sw = stats.shapiro(mod5.resid)
cen5 = {"C": 20, "M": 3, "V": 5, "S": 10}          # registros em um estado-ano (cenário)
novo = pd.DataFrame({"const": [1.0], **{k: [float(L(v))] for k, v in cen5.items()}})[["const"] + VARS]
pred5 = mod5.get_prediction(novo).summary_frame(alpha=0.05)
y5 = float(pred5["mean"].iloc[0])

R["q05"] = {
    "matriz_cov": cov_m.round(4).to_dict(), "matriz_cor": cor_m.round(3).to_dict(),
    "coef": {k: float(v) for k, v in mod5.params.items()},
    "p_coef": {k: float(v) for k, v in mod5.pvalues.items()},
    "ic95_coef": {k: [float(a), float(b)] for k, (a, b) in mod5.conf_int().iterrows()},
    "r2": float(mod5.rsquared), "r2_ajustado": float(mod5.rsquared_adj),
    "F": float(mod5.fvalue), "F_p": float(mod5.f_pvalue), "gl": [int(mod5.df_model), int(mod5.df_resid)],
    "erro_padrao_residual": float(np.sqrt(mod5.scale)),
    "vif": vif, "shapiro_residuos_p": float(res_sw.pvalue),
    "previsao_entrada": cen5, "previsao_E": y5, "previsao_registros": float(de_volta(y5)),
    "ip95_registros": [float(de_volta(pred5["obs_ci_lower"].iloc[0])), float(de_volta(pred5["obs_ci_upper"].iloc[0]))],
}
print("Matriz de covariância:\n", cov_m.round(4))
print("Matriz de correlação:\n", cor_m.round(3))
print(mod5.summary().tables[1])
eq = " + ".join(f"{mod5.params[v]:.4f}·{v}" for v in VARS)
print(f"Equação: E = {mod5.params['const']:.4f} + {eq}")
print(f"R² = {mod5.rsquared:.4f} | R² aj. = {mod5.rsquared_adj:.4f} | F({int(mod5.df_model)},{int(mod5.df_resid)}) = {mod5.fvalue:.2f} (p = {mod5.f_pvalue:.2e})")
print("VIF:", {k: round(v, 2) for k, v in vif.items()}, "| Shapiro dos resíduos p =", round(res_sw.pvalue, 4))
print(f"Previsão {cen5} -> {de_volta(y5):.1f} registros de enchente "
      f"(IP95%: {R['q05']['ip95_registros'][0]:.1f} a {R['q05']['ip95_registros'][1]:.1f})")

g = sns.pairplot(dados5, corner=True, plot_kws={"s": 14, "alpha": 0.5, "color": AZUL}, diag_kws={"color": AZUL})
g.figure.suptitle("Matriz de dispersão (escala log10(1+x))", y=1.01)
g.figure.savefig(os.path.join(FIG, "fig6_matriz_dispersao.png"), dpi=150, bbox_inches="tight")
plt.close(g.figure)

fig, ax = plt.subplots(figsize=(6, 4.8))
sns.heatmap(cor_m, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, square=True,
            cbar_kws={"label": "r de Pearson"}, ax=ax)
ax.set_title("Correlação de Pearson entre as variáveis")
salvar("fig7_correlacao_multivariada.png")

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.scatter(mod5.fittedvalues, mod5.resid, s=22, color=AZUL, alpha=0.6)
ax.axhline(0, color=VERMELHO, ls="--")
ax.set(title="Resíduos x valores ajustados (regressão múltipla)", xlabel="E ajustado", ylabel="Resíduo")
salvar("fig8_residuos.png")

# ----------------------------------------------------------------------------
# 06) Regressão logística binária: OBITO (>= 1 morte por enchente no UF-ano) ~ E + D + Dl
# ----------------------------------------------------------------------------
titulo("06) REGRESSÃO LOGÍSTICA BINÁRIA")
VARS6 = ["E", "D", "Dl"]
y6 = df["OBITO"]
X6 = sm.add_constant(df[VARS6])
modL = sm.Logit(y6, X6).fit(disp=0)
prob = modL.predict(X6)
vif6 = {v: float(variance_inflation_factor(X6.values, i)) for i, v in enumerate(X6.columns) if v != "const"}


def metricas(corte):
    pc = (prob >= corte).astype(int)
    m = confusion_matrix(y6, pc)
    tn, fp, fn, tp = m.ravel()
    return {"corte": corte, "VN": int(tn), "FP": int(fp), "FN": int(fn), "VP": int(tp),
            "acuracia": float((tn + tp) / m.sum()), "sensibilidade": float(tp / (tp + fn)),
            "especificidade": float(tn / (tn + fp)), "precisao": float(tp / (tp + fp)) if tp + fp else float("nan")}


m50, m30 = metricas(0.5), metricas(0.3)
cm = np.array([[m50["VN"], m50["FP"]], [m50["FN"], m50["VP"]]])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
acertos = []
for idx_tr, idx_te in cv.split(df[VARS6], y6):
    m_cv = sm.Logit(y6.iloc[idx_tr], X6.iloc[idx_tr]).fit(disp=0)
    p_te = m_cv.predict(X6.iloc[idx_te])
    acertos.append(float(((p_te >= 0.5).astype(int) == y6.iloc[idx_te]).mean()))
baseline = max(y6.mean(), 1 - y6.mean())

cenarios = {
    "Porte grande (25 registros, 3000 desabrigados, 12000 desalojados)": dict(E=25, D=3000, Dl=12000),
    "Porte médio (8 registros, 200 desabrigados, 1500 desalojados)": dict(E=8, D=200, Dl=1500),
    "Porte pequeno (2 registros, 0 desabrigados, 50 desalojados)": dict(E=2, D=0, Dl=50),
}
cen_res = {}
for nome, c in cenarios.items():
    xn = pd.DataFrame({"const": [1.0], **{k: [float(L(v))] for k, v in c.items()}})[["const"] + VARS6]
    p = float(modL.predict(xn).iloc[0])
    cen_res[nome] = {"prob_obito": p, "classe": "Com óbito" if p >= 0.5 else "Sem óbito"}

R["q06"] = {
    "coef": {k: float(v) for k, v in modL.params.items()},
    "p_coef": {k: float(v) for k, v in modL.pvalues.items()},
    "odds_ratio_por_dobro": {v: float(np.exp(modL.params[v] * np.log10(2))) for v in VARS6},
    "pseudo_r2_mcfadden": float(modL.prsquared), "LLR_p": float(modL.llr_pvalue), "vif": vif6,
    "corte_050": m50, "corte_030": m30,
    "acuracia_cv5_media": float(np.mean(acertos)), "acuracia_cv5_dp": float(np.std(acertos)),
    "acuracia_baseline": float(baseline),
    "cenarios": cen_res,
}
eqL = " + ".join(f"{modL.params[v]:.4f}·{v}" for v in VARS6)
print(modL.summary().tables[1])
print(f"Equação: ln(p/(1-p)) = {modL.params['const']:.4f} + {eqL}")
print("Matriz de confusão, corte 0,5 (linhas = real, colunas = previsto):\n", cm)
for m in (m50, m30):
    print(f"corte {m['corte']}: acurácia = {m['acuracia']:.4f} | sensibilidade = {m['sensibilidade']:.4f} | "
          f"especificidade = {m['especificidade']:.4f} | precisão = {m['precisao']:.4f}")
print(f"Acurácia em validação cruzada (5 pastas) = {np.mean(acertos):.4f} ± {np.std(acertos):.4f} | "
      f"referência (sempre prever 'sem óbito') = {baseline:.4f} | VIF = {({k: round(v, 1) for k, v in vif6.items()})}")
print("Razão de chances por dobro:", {v: round(R["q06"]["odds_ratio_por_dobro"][v], 2) for v in VARS6})
for nome, r in cen_res.items():
    print(f"  {nome}: P(óbito) = {r['prob_obito']:.3f} -> {r['classe']}")

fig, ax = plt.subplots(figsize=(4.8, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
            xticklabels=["Sem óbito", "Com óbito"], yticklabels=["Sem óbito", "Com óbito"])
ax.set(title=f"Matriz de confusão (acurácia = {m50['acuracia']:.1%})", xlabel="Previsto", ylabel="Real")
salvar("fig9_matriz_confusao.png")

# curva logística: P(óbito) vs registros de enchente, com D e Dl na média
fig, ax = plt.subplots(figsize=(7, 4))
regs = np.linspace(0, df.E.max(), 200)
grid = pd.DataFrame({"const": 1.0, "E": regs, "D": df.D.mean(), "Dl": df.Dl.mean()})[["const"] + VARS6]
ax.plot(de_volta(regs) + 1, modL.predict(grid), color=VERMELHO, lw=2.4, label="P(óbito) estimada (D e Dl na média)")
jit = np.random.default_rng(1).uniform(-0.03, 0.03, len(df))
ax.scatter(df.registros_enchentes + 1, y6 + jit, s=14, color=AZUL, alpha=0.5, label="UF-ano real (0 = sem, 1 = com óbito)")
ax.set_xscale("log")
ax.axhline(0.5, color=CINZA, ls="--", lw=1)
ax.set(title="Probabilidade de óbito x registros de enchente no estado-ano",
       xlabel="Registros de enchente (escala log; valor + 1)", ylabel="Probabilidade")
ax.legend(fontsize=8, loc="center left")
salvar("fig10_curva_logistica.png")

with open(os.path.join(PASTA, "resultados.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
titulo("FIM - figuras em ./figuras/ e números em resultados.json")
