path_lecaps = rpath_lecaps = r"C:\Users\gaspar.carra\Desktop\LECAPs-Quant-Strategy\data\BASE LECAPS.xlsx"
path_macro = r"C:\Users\gaspar.carra\Desktop\LECAPs-Quant-Strategy\data\SERIES TAMAR.REM.CCL16.5.xlsx"
path_futuros = r"C:\Users\gaspar.carra\closing_prices_contratos .xlsx"

dias_entrenamiento = [2,4]  # miércoles (2), viernes (4)
dia_recomendacion = 4      # viernes

top_n = 5  # recomendaciones"C:\Users\gaspar.carra\Desktop\LECAPs-Quant-Strategy\data\BASE LECAPS.xlsx"
path_macro = r"C:\Users\gaspar.carra\Desktop\LECAPs-Quant-Strategy\data\SERIES TAMAR.REM.CCL16.5.xlsx"
path_futuros = r"C:\Users\gaspar.carra\closing_prices_contratos .xlsx"

dias_entrenamiento = [2,4]  # miércoles (2), viernes (4)
dia_recomendacion = 4      # viernes

top_n = 5  # recomendaciones

import pandas as pd

def load_data(path_lecaps, path_macro, path_futuros, vencimientos,
              sheet_lecaps='Hoja1', sheet_futuros="Data"):

    # === LECAPS ===
    df_lecaps = pd.read_excel(path_lecaps, sheet_name=sheet_lecaps)
    df_lecaps.columns = df_lecaps.columns.str.strip().str.upper()

    df_lecaps['FECHA'] = pd.to_datetime(df_lecaps['FECHA'])
    df_lecaps['CIERRE'] = df_lecaps['CIERRE'].astype(str).str.replace(',', '.').astype(float)

    # === FUTUROS ===
    futuros_data = pd.read_excel(path_futuros, sheet_name=sheet_futuros)
    futuros_data['FECHA'] = pd.to_datetime(futuros_data['FECHA'])
    futuros_data['CONTRATOS'] = (
        futuros_data['CONTRATOS'].astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # === BADLAR ===
    df_badlar = pd.read_excel(path_macro, sheet_name="BADLAR")
    df_badlar.columns = df_badlar.columns.str.strip().str.upper()
    df_badlar.rename(columns={'VALOR': 'BADLAR'}, inplace=True)
    df_badlar['FECHA'] = pd.to_datetime(df_badlar['FECHA']).dt.normalize()

    # === INFLACION REM ===
    df_rem = pd.read_excel(path_macro, sheet_name="REM")
    df_rem.columns = df_rem.columns.str.strip().str.upper()
    df_rem['FECHA'] = pd.to_datetime(df_rem['FECHA'])
    df_rem['FECHA_PUBLICACION'] = (
    df_rem['FECHA'].dt.to_period('M').dt.to_timestamp('M') + pd.Timedelta(days=6)
    )
    df_rem['FECHA_PUBLICACION'] = df_rem['FECHA_PUBLICACION'].dt.normalize()
    df_rem = df_rem.sort_values('FECHA_PUBLICACION')
    df_rem = df_rem.drop_duplicates(subset="FECHA_PUBLICACION", keep="last")
    df_rem = df_rem.set_index('FECHA_PUBLICACION').resample('D').ffill().reset_index()

    # === CCL ===
    df_ccl = pd.read_excel(path_macro, sheet_name="CCL")
    df_ccl.columns = df_ccl.columns.str.strip().str.upper()
    df_ccl.rename(columns={'VALOR': 'SHOCK_CCL'}, inplace=True)
    df_ccl['FECHA'] = pd.to_datetime(df_ccl['FECHA']).dt.normalize()

    # === RIESGO PAÍS ===
    df_riesgo = pd.read_excel(path_macro, sheet_name="Riesgo_Pais")
    df_riesgo.columns = df_riesgo.columns.str.strip().str.upper()
    df_riesgo.rename(columns={'VALOR': 'RIESGO_PAIS'}, inplace=True)
    df_riesgo['FECHA'] = pd.to_datetime(df_riesgo['FECHA']).dt.normalize()

    # === BRECHA CAMBIARIA ===
    df_brecha = pd.read_excel(path_macro, sheet_name="Brecha_Cambiaria")
    df_brecha.columns = df_brecha.columns.str.strip().str.upper()
    df_brecha.rename(columns={'VALOR': 'BRECHA_CAMBIARIA'}, inplace=True)
    df_brecha['FECHA'] = pd.to_datetime(df_brecha['FECHA']).dt.normalize()

    # === LICITACIONES ===
        # === LICITACIONES ===
    df_lic = pd.read_excel(path_macro, sheet_name="Calendario de Licitaciones")
    df_lic.columns = df_lic.columns.str.strip().str.upper()

    # Extraer fechas de licitación
    fechas_licitaciones = pd.to_datetime(df_lic[df_lic["ES_LICITACION"] == "SI"]["FECHA"]).dt.normalize().dropna().unique().tolist()

    # Extraer fechas de liquidación
    fechas_liquidaciones = pd.to_datetime(df_lic[df_lic["ES_LIQUIDACIÓN"] == "SI"]["FECHA"]).dt.normalize().dropna().unique().tolist()



    # Canjes eliminados
    fechas_canjes = []

    # Estimar fecha de licitación si el calendario está desactualizado
    if not fechas_licitaciones or max(fechas_licitaciones) < pd.Timestamp.today():
        df_vencimientos = pd.DataFrame.from_dict(vencimientos, orient='index', columns=['FECHA_VTO'])
        df_vencimientos['FECHA_VTO'] = pd.to_datetime(df_vencimientos['FECHA_VTO'])
        prox_vto = df_vencimientos[df_vencimientos['FECHA_VTO'] >= pd.Timestamp.today()]['FECHA_VTO'].min()
        if pd.notnull(prox_vto):
            fecha_estimada = prox_vto - pd.Timedelta(days=7)
            fechas_licitaciones.append(fecha_estimada)

    return df_lecaps, futuros_data, df_badlar, df_rem, df_ccl, df_riesgo, df_brecha, fechas_licitaciones, fechas_canjes

    





def get_info_lecaps(path_info='LECAPS DATOS.xlsx'):
    df_info = pd.read_excel(path_info)
    df_info.columns = df_info.columns.str.strip().str.upper()
    df_info["TICKER"] = df_info["TICKER"].str.strip()
    df_info["EMISION"] = pd.to_datetime(df_info["EMISION"])
    df_info["VENCIMIENTO"] = pd.to_datetime(df_info["VENCIMIENTO"])
    df_info["VALOR_FINAL"] = df_info["VALOR_FINAL"].astype(str).str.replace(",", ".").astype(float)

    vencimientos = dict(zip(df_info["TICKER"], df_info["VENCIMIENTO"]))
    valores_finales = dict(zip(df_info["TICKER"], df_info["VALOR_FINAL"]))
    emisiones = dict(zip(df_info["TICKER"], df_info["EMISION"]))
            
                         

    return vencimientos, valores_finales, emisiones

from sklearn.preprocessing import StandardScaler
from hmmlearn.hmm import GaussianHMM

def entrenar_hmm(df_train, variables_hmm, n_regimenes=4):
    df_train = df_train.dropna(subset=variables_hmm).copy()
    df_train = df_train.sort_values("FECHA")

    scaler = StandardScaler()
    X = scaler.fit_transform(df_train[variables_hmm])

    modelo_hmm = GaussianHMM(
        n_components=n_regimenes,
        covariance_type="full",
        random_state=42,
        n_iter=500
    )
    modelo_hmm.fit(X)

    # ← Agregar predicción de régimen sobre el set de entrenamiento
    df_train["regimen"] = modelo_hmm.predict(X)

    # ← Devolver 3 valores como requiere tu pipeline
    return df_train, modelo_hmm, scaler



def aplicar_hmm(df, modelo_hmm, scaler, variables_hmm):
    df_ap = df.dropna(subset=variables_hmm).copy()
    df_ap = df_ap.sort_values("FECHA")
    
    # Normalizar fecha
    df_ap["FECHA"] = pd.to_datetime(df_ap["FECHA"]).dt.normalize()
    df["FECHA"] = pd.to_datetime(df["FECHA"]).dt.normalize()

    X = scaler.transform(df_ap[variables_hmm])
    regimes = modelo_hmm.predict(X)

    df_resultado = df_ap[["FECHA"]].copy()
    df_resultado["regimen"] = regimes

    # Merge
    df_resultado = df_resultado.drop_duplicates(subset=["FECHA"])
    df_merged = df.merge(df_resultado, on="FECHA", how="left")


    return df_merged

def agregar_regimen_siguiente(df, modelo_hmm):
    transmat = modelo_hmm.transmat_
    
    def regime_next(r):
        if r >= 0:
            return np.argmax(transmat[int(r)])
        else:
            return -1
    
    df = df.copy()
    df['regimen_siguiente_predicho'] = df['regimen'].apply(regime_next)

    for i in range(transmat.shape[0]):
        df[f'prob_regimen_siguiente_{i}'] = df['regimen'].apply(lambda r: transmat[int(r)][i] if r >= 0 else 0)
    
    return df

def preparar_dataset(
    df_lecaps,
    futuros_data,
    df_badlar,
    df_rem,
    df_ccl,
    df_riesgo,
    df_brecha,
    fechas_licitaciones,
    fechas_canjes,
    vencimientos,
    valores_finales,
    emisiones,
    variables_hmm,
    n_regimenes=3
):
    df = df_lecaps.copy()

    # === 1. MERGE DATOS EXTERNOS ===
    df = df.merge(df_badlar, on="FECHA", how="left")
    df = df.merge(df_rem, on="FECHA", how="left")
    df = df.merge(df_ccl, on="FECHA", how="left")
    df = df.merge(df_riesgo, on="FECHA", how="left")
    df = df.merge(df_brecha, on="FECHA", how="left")
    df = df.merge(futuros_data, on="FECHA", how="left")

    # === 2. DATOS ESTRUCTURALES ===
    df = agregar_dias_a_liquidacion(df, fechas_licitaciones)
    df["es_canje"] = df["FECHA"].isin(fechas_canjes).astype(int)
    df["VALOR_FINAL"] = df["SIMBOLO"].map(valores_finales)
    df["EMISION"] = df["SIMBOLO"].map(emisiones)
    df["DIAS_AL_VTO"] = (df["VTO"] - df["FECHA"]).dt.days
    df["PLAZO_TOTAL"] = (df["VTO"] - df["EMISION"]).dt.days
    df["DURACION"] = df["DIAS_AL_VTO"] / df["PLAZO_TOTAL"]

    # === 3. ENRIQUECIMIENTOS ===
    df = agregar_momentum_curva(df)
    df = agregar_slope_local(df)
    df = agregar_score_manual(df)
    df = agregar_info_vencimientos(df)
    df = calcular_ytl_rolling(df, horizon=5, col_price="VWAP")
    
    # PCA features
    features_pca = ["TIR", "Roll", "Curvatura", "ModifiedDuration", "Convexidad"]
    df = agregar_pca_features(df, features_pca=features_pca, n_components=3)

    # === 4. REGÍMENES (HMM) ===
    df = entrenar_modelo_hmm(df, variables=variables_hmm, n_regimenes=n_regimenes)

    # === 5. CUANTILES y Expected Shortfall ===
    all_features = [
        'TIR', 'Roll', 'Curvatura', 'ModifiedDuration', 'Convexidad',
        'vol_tir_5d', 'tasa_min_fut', 'tasa_max_fut', 'tasa_avg_fut', 'vol_fut',
        'Slope_Futuro', 'spread_TIR_Badlar', 'spread_TIR_INF',
        'RIESGO_PAIS', 'BRECHA_CAMBIARIA', 'score_manual'
    ]
    df = entrenar_quantile_features(df, features=all_features, quantiles=[0.1, 0.9], horizon=5)

    # === 6. TARGETS ===
    df_modelo = generate_targets_and_lags(df.copy(), entrenamiento=True)
    df_full = generate_targets_and_lags(df.copy(), entrenamiento=False)

    # === 7. FEATURES PARA MODELO ===
    X_modelo, y_modelo, features = build_model_dataset(df_modelo, n_regimenes=n_regimenes)
    df_modelo = X_modelo.copy()
    df_modelo["ret_futuro_5d"] = y_modelo

    return df_full, df_modelo, features



   # ✅ Primero, definir la función FUERA de preparar_dataset
  # ✅ Primero, definir la función FUERA de preparar_dataset
# 1. Definir la función al principio
# ✅ 1. Definir correctamente la función (fuera de cualquier otra función)
def calcular_ret_futuro(df, dias=5):
    df = df.sort_values(["SIMBOLO", "FECHA"])
    df["CIERRE_FUTURO"] = df.groupby("SIMBOLO")["CIERRE"].shift(-dias)
    df["ret_futuro_5d"] = (df["CIERRE_FUTURO"] / df["CIERRE"]) - 1
    return df

# ✅ 2. Correr tu dataset como siempre
df_lecaps_full, df_modelo, features = preparar_dataset(
    df_lecaps, futuros_data, df_badlar, df_rem, df_ccl, df_riesgo, df_brecha,
    fechas_licitaciones, fechas_canjes,
    vencimientos, valores_finales, emisiones,
    variables_hmm=None, n_regimenes=4
)

# ✅ 3. Aplicar la función Y reasignar el resultado
df_lecaps_full = calcular_ret_futuro(df_lecaps_full, dias=5)

# ✅ 4. Verificar que funcione
print("ret_futuro_5d" in df_lecaps_full.columns)  # Debería ser True
print(df_lecaps_full[["SIMBOLO", "FECHA", "CIERRE", "CIERRE_FUTURO", "ret_futuro_5d"]].tail())










import pandas as pd
import numpy as np
from scipy.interpolate import UnivariateSpline

def clean_lecaps_data(df_lecaps, vencimientos, valores_finales, emisiones):
    vto_df = pd.DataFrame.from_dict(vencimientos, orient='index', columns=['VTO']).reset_index()
    vto_df.columns = ['SIMBOLO', 'VTO']
    vto_df['VTO'] = pd.to_datetime(vto_df['VTO'])

    vf_df = pd.DataFrame.from_dict(valores_finales, orient='index', columns=['VALOR_FINAL']).reset_index()
    vf_df.columns = ['SIMBOLO', 'VALOR_FINAL']
# Ya no hace falta convertir aquí porque valores_finales son floats

    emision_df = pd.DataFrame.from_dict(emisiones, orient='index', columns=['EMISION']).reset_index()
    emision_df.columns = ['SIMBOLO', 'EMISION']
    emision_df['EMISION'] = pd.to_datetime(emision_df['EMISION'])

    df = df_lecaps.drop(columns=['VTO', 'VALOR_FINAL', 'EMISION'], errors='ignore')
    df = df.merge(vto_df, on='SIMBOLO', how='left')
    df = df.merge(vf_df, on='SIMBOLO', how='left')
    df = df.merge(emision_df, on='SIMBOLO', how='left')

    df['DIAS_AL_VTO'] = (df['VTO'] - df['FECHA']).dt.days
    df['PLAZO_TOTAL'] = (df['VTO'] - df['EMISION']).dt.days
    df['DURACION'] = df['DIAS_AL_VTO'] / 365
    df['TIR'] = (df['VALOR_FINAL'] / df['CIERRE'] - 1) / df['DIAS_AL_VTO'] * 365
    df['carry'] = df['TIR']
    df['Roll'] = df['carry'] * df['DURACION']
    df['Curvatura'] = df.groupby('FECHA')['TIR'].transform(
    lambda x: x - x.rolling(3, center=True, min_periods=1).mean()
    )

    return df

def apply_spline_features(df):
    df['ModifiedDuration'] = df['DURACION']
    df['Convexidad'] = df['DURACION'] ** 2
    df['Slope'] = df.groupby('FECHA')['TIR'].transform(lambda x: x.diff().fillna(0))

# Calcular TIR_VWAP usando VWAP como precio (más realista)
    df['TIR_VWAP'] = (df['VALOR_FINAL'] / df['VWAP'] - 1) / df['DIAS_AL_VTO'] * 365
    return df


import numpy as np
from numpy.polynomial.polynomial import polyfit
from scipy.interpolate import UnivariateSpline

def agregar_features_curva(df):
    df = df.copy()
    resultados = []

    for fecha in df["FECHA"].dropna().unique():
        df_dia = df[df["FECHA"] == fecha].copy()
    
        if len(df_dia) < 5:
            continue
    
        x = df_dia["DIAS_AL_VTO"]
        y = df_dia["TIR_VWAP"]
    
        # Evitar problemas de NaNs
        mask_valid = x.notna() & y.notna()
        x = x[mask_valid]
        y = y[mask_valid]
        df_dia = df_dia.loc[mask_valid].copy()
    
        df_dia["Roll"] = df_dia["TIR_VWAP"] * df_dia["DURACION"]
    
        try:
            coefs = polyfit(x, y, deg=2)
            df_dia["TIR_fit"] = coefs[0] + coefs[1]*x + coefs[2]*(x**2)
            df_dia["spread_vs_fit"] = df_dia["TIR_VWAP"] - df_dia["TIR_fit"]
        except:
            df_dia["TIR_fit"] = np.nan
            df_dia["spread_vs_fit"] = np.nan
    
        try:
            spline = UnivariateSpline(x, y, k=3, s=0.0005)
            df_dia["TIR_spline"] = spline(x)
            df_dia["spread_vs_spline"] = df_dia["TIR_VWAP"] - df_dia["TIR_spline"]
        except:
            df_dia["TIR_spline"] = np.nan
            df_dia["spread_vs_spline"] = np.nan
    
        # Calcular z-score con std > 0
        std_spread = df_dia["spread_vs_fit"].std()
        if std_spread and std_spread > 0:
            df_dia["z_spread_vs_fit"] = (df_dia["spread_vs_fit"] - df_dia["spread_vs_fit"].mean()) / std_spread
        else:
            df_dia["z_spread_vs_fit"] = np.nan
    
        # Rankings
        df_dia["rank_tir"] = df_dia["TIR_VWAP"].rank(method="first", ascending=False)
        df_dia["rank_roll"] = df_dia["Roll"].rank(method="first", ascending=False)
        df_dia["rank_spread_fit"] = df_dia["spread_vs_fit"].rank(method="first", ascending=False)
    
        resultados.append(df_dia)
    
    return pd.concat(resultados, ignore_index=True) if resultados else df.copy()




def process_futuros_data(futuros_data):
   futuros_data = futuros_data.copy()
   futuros_data['FECHA'] = pd.to_datetime(futuros_data['FECHA'])

# Asegurarse de que "T. IMPLICITA" está en porcentaje
   futuros_data['T. IMPLICITA'] = pd.to_numeric(futuros_data['T. IMPLICITA'], errors='coerce') / 100

# Derivar VTO desde el nombre del contrato
   futuros_data['VTO'] = pd.to_datetime(
    futuros_data['TIPO CONTRATO'].str.extract(r'(\d{6})')[0],
    format='%m%Y', errors='coerce'
   ) + pd.offsets.MonthEnd(0)

   futuros_data['DIAS_AL_VTO'] = (futuros_data['VTO'] - futuros_data['FECHA']).dt.days

   curva_fut = futuros_data.groupby('FECHA')['T. IMPLICITA'].agg(['min', 'max', 'mean', 'std']).reset_index()
   curva_fut.columns = ['FECHA', 'tasa_min_fut', 'tasa_max_fut', 'tasa_avg_fut', 'vol_fut']
   curva_fut['Slope_Futuro'] = curva_fut['tasa_max_fut'] - curva_fut['tasa_min_fut']

   return curva_fut


def merge_futuros_lecaps(df_lecaps, curva_fut):
    curva_fut = curva_fut.drop_duplicates(subset=["FECHA"])
    df_lecaps = df_lecaps.drop(columns=['tasa_min_fut', 'tasa_max_fut', 'tasa_avg_fut', 'vol_fut', 'Slope_Futuro'], errors='ignore')
    df_lecaps = df_lecaps.merge(curva_fut, on='FECHA', how='left')
    return df_lecaps

def add_macro_and_events(df_lecaps, df_badlar, df_rem, df_ccl, df_riesgo, df_brecha,
                     fechas_licitaciones, fechas_canjes=None):

    df = df_lecaps.copy()   # ← IMPORTANTE: inicializa df
    
    # Preprocesamiento mínimo
    df_badlar = df_badlar.drop_duplicates(subset=["FECHA"])
    df_rem = df_rem.drop_duplicates(subset=["FECHA"])
    df_ccl = df_ccl.drop_duplicates(subset=["FECHA"])
    df_riesgo = df_riesgo.drop_duplicates(subset=["FECHA"])
    df_brecha = df_brecha.drop_duplicates(subset=["FECHA"])
    
    # Macros
    df = df.merge(df_badlar, on="FECHA", how="left")
    df = df.merge(df_rem, on="FECHA", how="left")
    df = df.merge(df_ccl, on="FECHA", how="left")
    df = df.merge(df_riesgo, on="FECHA", how="left")
    df = df.merge(df_brecha, on="FECHA", how="left")

    # === Crear spread TIR - Inflación ===
    df["spread_TIR_INF"] = df["TIR_VWAP"] - df["INFLACION_REM_ANUAL"]
        # Calcular spreads luego del merge
    df["spread_TIR_Badlar"] = df["TIR"] - df["BADLAR"]
    df["spread_TIR_INF"] = df["TIR"] - df["INFLACION_REM_ANUAL"]


# Eventos
    df["dias_a_licitacion"] = df["FECHA"].apply(
        lambda f: min([(lic - f).days for lic in fechas_licitaciones if lic >= f], default=None)
    )
    
    if fechas_canjes and len(fechas_canjes) > 0:
        df["es_canje"] = df["FECHA"].isin(fechas_canjes).astype(int)
    else:
        df["es_canje"] = 0

    
    return df

def calcular_target(df, col_precio='VWAP', horizon=5):
    df = df.sort_values(['SIMBOLO', 'FECHA']).copy()
    
    # Asegurate de que la columna de precios existe
    if col_precio not in df.columns:
        raise ValueError(f"La columna de precios '{col_precio}' no está en el dataframe.")
    
    # Calcular el retorno futuro a 'horizon' días
    df['precio_futuro'] = df.groupby('SIMBOLO')[col_precio].shift(-horizon)
    df['ret_futuro_5d'] = (df['precio_futuro'] / df[col_precio]) - 1
    
    return df




def generate_targets_and_lags(df, entrenamiento=True):
    df = df.sort_values(['SIMBOLO', 'FECHA'])
    
    # Siempre calculamos los lags
    df['TIR_lag1'] = df.groupby('SIMBOLO')['TIR'].shift(1)
    df['Roll_lag1'] = df.groupby('SIMBOLO')['Roll'].shift(1)
    df['Curvatura_lag1'] = df.groupby('SIMBOLO')['Curvatura'].shift(1)
    df['vol_tir_5d'] = df.groupby('SIMBOLO')['TIR'].transform(lambda x: x.rolling(5).std())
    
    if entrenamiento:
        col_precio = 'VWAP' if 'VWAP' in df.columns else 'CIERRE'
        df = calcular_target(df, col_precio=col_precio, horizon=5)
    
        df['rank'] = df.groupby('FECHA')['ret_futuro_5d'].rank(method='first', ascending=False)
        df['target_rank'] = (df['rank'] <= 5).astype(int)
        df['ret_5d_lag1'] = df.groupby('SIMBOLO')['ret_futuro_5d'].shift(1)
    
    df = df.drop_duplicates(subset=["SIMBOLO", "FECHA"])
    return df

from lightgbm import LGBMRegressor

def entrenar_quantile_features(df, features, quantiles=[0.1, 0.9], horizon=5):
    df_q = df.dropna(subset=['ret_futuro_5d'] + features).copy()
    
    resultados = {f'ret_p{int(q*100)}': [] for q in quantiles}
    resultados['expected_shortfall'] = []
    
    fechas = sorted(df_q["FECHA"].unique())
    
    for fecha in fechas:
        df_test = df_q[df_q["FECHA"] == fecha].copy()
        df_train = df_q[df_q["FECHA"] < fecha].copy()
    
        if df_train.shape[0] < 50:
            continue
    
        X_train = df_train[features]
        y_train = df_train['ret_futuro_5d']
        X_test = df_test[features]
    
        for q in quantiles:
            model = LGBMRegressor(objective='quantile', alpha=q, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            col_name = f'ret_p{int(q*100)}'
            df_q.loc[df_test.index, col_name] = y_pred
    
        # Expected Shortfall (mean of bottom 10%)
        y_bottom = df_train['ret_futuro_5d'].nsmallest(int(len(y_train) * 0.1))
        es_value = y_bottom.mean() if len(y_bottom) > 0 else np.nan
        df_q.loc[df_test.index, 'expected_shortfall'] = es_value
    
    return df.merge(df_q[['FECHA', 'SIMBOLO', 'ret_p10', 'ret_p90', 'expected_shortfall']], on=["FECHA", "SIMBOLO"], how="left")

# === Funciones auxiliares top-tier ===

from numpy.polynomial.polynomial import polyfit

def agregar_momentum_curva(df):
    df = df.copy()
    slopes = []
    for fecha in df["FECHA"].dropna().unique():
        df_dia = df[df["FECHA"] == fecha].copy()
        if len(df_dia) < 5:
            continue
        try:
            coefs = polyfit(df_dia["DIAS_AL_VTO"], df_dia["TIR_VWAP"], deg=1)
            slopes.append((fecha, coefs[1]))
        except:
            continue
    df_slope = pd.DataFrame(slopes, columns=["FECHA", "curva_slope"])
    df_slope["curva_slope_5d"] = df_slope["curva_slope"].rolling(5).mean()
    df_slope["curva_slope_change"] = df_slope["curva_slope"] - df_slope["curva_slope_5d"]
    df = df.merge(df_slope, on="FECHA", how="left")
    df["curva_aplana"] = (df["curva_slope_change"] < 0).astype(int)
    df["curva_empina"] = (df["curva_slope_change"] > 0).astype(int)
    return df

def agregar_score_manual(df):
    df = df.copy()

    # 🆕 Calcular Roll_z si no existe
    if "Roll_z" not in df.columns:
        df["Roll_z"] = df.groupby("FECHA")["Roll"].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )

    df["rank_roll_z"] = df.groupby("FECHA")["Roll_z"].rank(method="first", ascending=False)
    df["rank_spread_fit"] = df.groupby("FECHA")["spread_vs_fit"].rank(method="first", ascending=False)
    df["rank_tir"] = df.groupby("FECHA")["TIR_VWAP"].rank(method="first", ascending=False)
    df["liq_pctil"] = df.groupby("FECHA")["MONTO_NEGOCIADO"].rank(pct=True)
    df["penal_liquidez"] = (1 - df["liq_pctil"])
    
    df["score_manual"] = (
        0.4 * df["rank_roll_z"] +
        0.4 * df["rank_spread_fit"] +
        0.2 * df["rank_tir"] -
        0.5 * df["penal_liquidez"]
    )
    
    return df


def agregar_dias_a_liquidacion(df, fechas_liquidaciones):
    df = df.copy()
    fechas_liquidaciones = sorted(pd.to_datetime(fechas_liquidaciones))
    
    def prox_liq(fecha):
        futuras = [liq for liq in fechas_liquidaciones if liq >= fecha]
        return (futuras[0] - fecha).days if futuras else None
    
    df["dias_a_liquidacion"] = df["FECHA"].apply(prox_liq)
    return df


def agregar_info_vencimientos(df):
    df = df.copy()
    df["prox_vto_general"] = df.groupby("FECHA")["DIAS_AL_VTO"].transform("min")
    df["es_el_mas_corto"] = (df["DIAS_AL_VTO"] == df["prox_vto_general"]).astype(int)
    df["max_vto"] = df.groupby("FECHA")["DIAS_AL_VTO"].transform("max")
    df["es_el_mas_largo"] = (df["DIAS_AL_VTO"] == df["max_vto"]).astype(int)
    df["std_dias_vto"] = df.groupby("FECHA")["DIAS_AL_VTO"].transform("std")
    df["concentracion_vto"] = 1 / (df["std_dias_vto"] + 1e-6)
    return df
def agregar_slope_local(df):
        df = df.copy()
        df = df.sort_values(["FECHA", "DIAS_AL_VTO"])
        df["TIR_siguiente"] = df.groupby("FECHA")["TIR_VWAP"].shift(-1)
        df["DIAS_siguiente"] = df.groupby("FECHA")["DIAS_AL_VTO"].shift(-1)
        
        df["slope_local"] = (df["TIR_siguiente"] - df["TIR_VWAP"]) / (df["DIAS_siguiente"] - df["DIAS_AL_VTO"] + 1e-6)
        return df
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def agregar_pca_features(df, features_pca, n_components=3):
        df = df.copy()
        scaler = StandardScaler()
        pca = PCA(n_components=n_components)
        
        fechas = df["FECHA"].unique()
        resultados = []
        for fecha in fechas:
            df_dia = df[df["FECHA"] == fecha].copy()
            if len(df_dia) < n_components:
                continue
        
            X = scaler.fit_transform(df_dia[features_pca])
            comps = pca.fit_transform(X)
        
            for i in range(n_components):
                df_dia[f"pca_{i+1}"] = comps[:, i]
        
            resultados.append(df_dia)
    
        return pd.concat(resultados).reset_index(drop=True)
    
def calcular_ytl_rolling(df, horizon=5, col_price="VWAP"):
    df = df.copy()
    df = df.sort_values(["FECHA", "SIMBOLO"])

    # Validación
    if col_price not in df.columns:
        raise ValueError(f"❌ Falta la columna de precio: {col_price}")
    
    ytl_resultados = []
    fechas = sorted(df["FECHA"].unique())
    
    for i in range(len(fechas) - horizon):
        f_actual = fechas[i]
        f_futuro = fechas[i + horizon]
    
        df_today = df[df["FECHA"] == f_actual].copy()
        df_next = df[df["FECHA"] == f_futuro].copy()
    
        if df_today.empty or df_next.empty:
            continue
    
        # Elegimos el bono con mejor score manual como "el que rolás"
        top_hoy = df_today.sort_values("score_manual", ascending=False).iloc[0]
        ticker = top_hoy["SIMBOLO"]
        precio_hoy = top_hoy[col_price]
    
        next_row = df_next[df_next["SIMBOLO"] == ticker]
        if not next_row.empty:
            precio_fut = next_row.iloc[0][col_price]
            ret = (precio_fut / precio_hoy - 1)
            ret_anualizado = ((1 + ret) ** (365 / horizon)) - 1
            ytl_resultados.append((f_actual, ret_anualizado))
    
    df_ytl = pd.DataFrame(ytl_resultados, columns=["FECHA", "ytl_5d"])
    df = df.merge(df_ytl, on="FECHA", how="left")
    
    return df




def build_model_dataset(df, n_regimenes=4, incluir_pca=True):
    df = df.copy()

    base_features = [
        'TIR', 'Roll', 'Curvatura', 'ModifiedDuration', 'Convexidad', 'Slope',
        'vol_tir_5d', 'tasa_min_fut', 'tasa_max_fut', 'tasa_avg_fut', 'vol_fut',
        'Slope_Futuro', 'TIR_lag1', 'Roll_lag1', 'Curvatura_lag1',
        'BADLAR', 'INFLACION_REM_ANUAL', 'SHOCK_CCL',
        'spread_TIR_Badlar', 'spread_TIR_INF', 'dias_a_licitacion', 'es_canje',
        'RIESGO_PAIS', 'BRECHA_CAMBIARIA', 'regimen',
        'cambio_regimen', 'dias_en_regimen','spread_vs_fit', 'z_spread_vs_fit',
        'rank_tir', 'rank_roll','curva_slope', 'curva_slope_change', 'curva_aplana', 'curva_empina',
        'rank_roll_z', 'rank_spread_fit', 'liq_pctil', 'penal_liquidez', 'score_manual',
        'es_el_mas_corto', 'es_el_mas_largo', 'concentracion_vto', 'ytl_5d',
        'ret_p10', 'ret_p90', 'expected_shortfall'
    ]
    
    # ➕ Interacciones con regímenes
    for var in ['TIR', 'Roll', 'Curvatura', 'BADLAR', 'spread_TIR_Badlar']:
        base_features.extend([f"{var}_reg{r}" for r in range(n_regimenes)])
    
    # ➕ Probabilidades de régimen siguiente
    base_features.append('regimen_siguiente_predicho')
    base_features.extend([f'prob_regimen_siguiente_{r}' for r in range(n_regimenes)])

    # ➕ Componentes PCA si se desea
    if incluir_pca:
        base_features += ['pca_1', 'pca_2', 'pca_3']
    
    # 🔍 Chequear si faltan columnas
    faltan = [f for f in base_features if f not in df.columns]
    if faltan:
        print("⚠️ Faltan estas columnas en el DataFrame:")
        for f in faltan:
            print(f"   - {f}")
    
    # ✅ Quedarse solo con las columnas que están
    features = [f for f in base_features if f in df.columns]
    X = df[features].copy()
    y = df['ret_futuro_5d'].copy() if 'ret_futuro_5d' in df.columns else None

    # ❗Chequear NaNs
    nans = X.isna().sum()
    nans = nans[nans > 0]
    if not nans.empty:
        print("⚠️ Columnas con NaNs en las features:")
        print(nans)
    
    return X, y, features

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def entrenar_modelos(df_modelo, features):
    df_entrena = df_modelo.dropna(subset=['ret_futuro_5d'] + features).copy()
    
    X_train = df_entrena[features]
    y_train = df_entrena['ret_futuro_5d']

    modelo = Pipeline([
        ('scaler', StandardScaler()),
        ('reg', Ridge(alpha=1.0))
    ])

    modelo.fit(X_train, y_train)

    print("✅ Modelo entrenado")
    return modelo

def predecir_top_n(df, modelo, features, top_n=5):
    df_pred = df.copy()
    df_pred = df_pred.dropna(subset=features)
    df_pred['ret_esperado'] = modelo.predict(df_pred[features])

    df_top = df_pred.sort_values(['FECHA', 'ret_esperado'], ascending=[True, False]) \
                    .groupby('FECHA') \
                    .head(top_n) \
                    .copy()
    
    return df_top

def generar_reporte(df_top):
    print("🧾 Recomendaciones Top LECAPs:")
    print(df_top[['FECHA', 'SIMBOLO', 'TIR', 'ret_esperado']].tail(10))
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
import numpy as np
import pandas as pd
import joblib

def calcular_umbral_std(df, features, ventana=60, min_datos=20):
    df = df.sort_values("FECHA")
    fechas = sorted(df["FECHA"].unique())
    std_sums = []

    for i in range(ventana, len(fechas) - 1):
        fechas_train = fechas[i - ventana:i]
        df_train = df[df["FECHA"].isin(fechas_train)].copy()

        if df_train.shape[0] < min_datos:
            continue

        features_existentes = [f for f in features if f in df_train.columns]
        X_train = df_train[features_existentes].copy()
        X_train = X_train.applymap(lambda x: np.nan if not pd.api.types.is_number(x) else x).astype(float)

        if X_train.dropna().shape[0] < min_datos:
            continue

        std_total = X_train.std().sum(skipna=True)
        if not np.isnan(std_total):
            std_sums.append(std_total)

    return np.percentile(std_sums, 10) if std_sums else 0.01

def entrenar_modelos_regresion(df, features, ventana=30, n_regimenes=4):
    df = df.sort_values("FECHA")
    fechas = sorted(df["FECHA"].unique())
    resultados = []
    modelos_entrenados = {}

    # ✅ Umbral dinámico basado en tus datos históricos
    umbral_dinamico = calcular_umbral_std(df, features, ventana)
    print(f"📊 Umbral dinámico (percentil 10): {umbral_dinamico:.2f}")

    for i in range(ventana, len(fechas) - 1):
        fechas_train = fechas[i - ventana:i]
        fecha_test = fechas[i]

        df_train = df[df["FECHA"].isin(fechas_train)].copy()
        df_test = df[df["FECHA"] == fecha_test].copy()

        df_train = df_train[~df_train["ret_futuro_5d"].isna()].copy()
        if df_train.shape[0] < 20:
            print(f"⚠️ Skip {fecha_test.date()} - pocos datos ({df_train.shape[0]})")
            continue

        features_existentes = [f for f in features if f in df_train.columns]
        X_train = df_train[features_existentes].copy()
        y_train = df_train["ret_futuro_5d"]
        X_test = df_test[features_existentes].copy()

        X_train = X_train.applymap(lambda x: np.nan if not pd.api.types.is_number(x) else x).astype(float)
        X_test = X_test.applymap(lambda x: np.nan if not pd.api.types.is_number(x) else x).astype(float)

        # ❌ Filtro por baja varianza
        std_sum = X_train.std().sum()
        if std_sum < umbral_dinamico:
            print(f"❌ Baja variabilidad en {fecha_test} – std sum: {std_sum:.2f}")
            continue

        # Imputación
        imputer = IterativeImputer(random_state=42)
        X_train_imp = pd.DataFrame(imputer.fit_transform(X_train), columns=features_existentes, index=X_train.index)
        X_test_imp = pd.DataFrame(imputer.transform(X_test), columns=features_existentes, index=X_test.index)

        modelos = {
            "catboost": CatBoostRegressor(verbose=0, random_state=42),
            "lightgbm": LGBMRegressor(random_state=42)
        }

        predicciones = []
        for nombre, modelo in modelos.items():
            modelo.fit(X_train_imp, y_train)
            y_pred = modelo.predict(X_test_imp)
            predicciones.append(y_pred)
            modelos_entrenados[nombre] = modelo

        ret_esperado = np.mean(predicciones, axis=0)
        df_resultado = df_test.copy()
        df_resultado["ret_esperado"] = ret_esperado
        resultados.append(df_resultado)

    df_backtest = pd.concat(resultados).reset_index(drop=True)
    df_backtest = df_backtest.drop_duplicates(subset=["SIMBOLO", "FECHA"])
    
    # ❗Cuidado con nombres de columnas como "MONTO_NEGOCIADO" vs "MONTO NEGOCIADO"
    if "MONTO_NEGOCIADO" in df_backtest.columns:
        df_backtest = df_backtest[df_backtest["MONTO_NEGOCIADO"] > 0]

    # Imputador final (solo features válidas)
    features_validas = [f for f in features if f in df.columns and df[f].notna().sum() > 0]
    X_total = df[features_validas].copy().applymap(lambda x: np.nan if not pd.api.types.is_number(x) else x).astype(float)
    
    imputer_final = IterativeImputer(random_state=42)
    imputer_final.fit(X_total)
    
    joblib.dump(imputer_final, "imputer.pkl")
    joblib.dump(modelos_entrenados, "modelos_finales.pkl")

    with open("n_regimenes_backtest.txt", "w") as f:
        f.write(str(n_regimenes))

    print(f"✅ Backtest completado sobre {len(resultados)} fechas")
    return df_backtest

def calcular_retornos_por_decil(df_backtest, score_col='ret_esperado', real_col='ret_futuro_5d', n_bins=10):
    df = df_backtest.copy()
    
    # Ordenar por la predicción
    df['score_bin'] = pd.qcut(df[score_col], q=n_bins, labels=False, duplicates='drop')

    resumen = df.groupby('score_bin').agg(
        count=(real_col, 'count'),
        retorno_real_promedio=(real_col, 'mean'),
        retorno_esperado_promedio=(score_col, 'mean'),
        std_ret_real=(real_col, 'std'),
        sharpe_aprox=lambda g: g.mean() / g.std() if g.std() > 0 else np.nan
    ).reset_index()

    print("📊 Evaluación por decil de score:")
    print(resumen)

    return resumen

def calcular_hit_rate_por_regimen_ventana(df_hist, ventana, fecha_ref):
    fecha_ref = pd.to_datetime(fecha_ref)
    fecha_ini = fecha_ref - pd.Timedelta(days=ventana)

    df_hist = df_hist.copy()
    df_hist["FECHA"] = pd.to_datetime(df_hist["FECHA"], errors="coerce")

    df_filtrado = df_hist[
        (df_hist["FECHA"] >= fecha_ini) &
        (df_hist["FECHA"] < fecha_ref)
    ]

    hit_rates = df_filtrado.groupby("regimen")["ret_futuro_5d"].mean().to_dict()


    # Obtener la cantidad de regímenes según las columnas existentes
    n_regimenes = max(df_hist["regimen"].dropna().astype(int).unique()) + 1

    return [hit_rates.get(r, 0.0) for r in range(n_regimenes)]
def optimizar_exposicion_por_regimen(hit_rates, probs_regimen, exposiciones_prev, alpha=0.5):
    hit_rates = np.array(hit_rates)
    probs_regimen = np.array(probs_regimen)
    exposiciones_prev = np.array(exposiciones_prev)

    # Ponderar hit_rates por probabilidad actual del régimen
    ponderados = hit_rates * probs_regimen

    if ponderados.sum() == 0:
        nuevas_exposiciones = exposiciones_prev
    else:
        nuevas_exposiciones = ponderados / ponderados.sum()

    exposiciones_suavizadas = alpha * nuevas_exposiciones + (1 - alpha) * exposiciones_prev
    return exposiciones_suavizadas
def predecir_top_5_con_regimen_adaptativo(df, features, top_n=5, path_csv=None, df_backtest_hist=None, ventana=60, exposiciones_prev=None):
    df = df.copy()
    df = df.sort_values("FECHA")
    
    # Validar consistencia
    with open("n_regimenes_backtest.txt", "r") as f:
        n_reg_backtest = int(f.read())
    
    n_reg_actual = df["regimen"].nunique()
    if n_reg_actual != n_reg_backtest:
        raise ValueError(f"❌ Inconsistencia: el modelo fue entrenado con {n_reg_backtest} regímenes, pero el dataset tiene {n_reg_actual}.")

    # 👉 Cargar modelos entrenados
    modelos = joblib.load("modelos_finales.pkl")

    # 👉 Cargar imputador
    imputer = joblib.load("imputer.pkl")

    fechas = sorted(df["FECHA"].unique())
    resultados = []

    for i in range(ventana, len(fechas)):
        fechas_train = fechas[i - ventana:i]
        fecha_actual = fechas[i]

        df_train = df[df["FECHA"].isin(fechas_train)].copy()
        df_actual = df[df["FECHA"] == fecha_actual].copy()

        X = df_actual[features].copy()
        X = X.applymap(lambda x: np.nan if not pd.api.types.is_number(x) or pd.isna(x) else x).astype(float)
        X = pd.DataFrame(imputer.transform(X), columns=features, index=X.index)

        # ⚠️ Usar todos los modelos
        ret_esperado = [modelo.predict(X) for modelo in modelos.values()]
        df_actual["ret_esperado"] = np.mean(ret_esperado, axis=0)

        df_actual = df_actual.sort_values("ret_esperado", ascending=False)
        df_top = df_actual.head(top_n)
        resultados.append(df_top)

    df_backtest = pd.concat(resultados).reset_index(drop=True)

    if path_csv:
        df_backtest.to_csv(path_csv, index=False)

    return df_backtest
import os
import pandas as pd

def resetear_si_inconsistente(n_reg_opt, df_modelo, features):
    ruta_backtest = "backtest_lecaps.csv"
    ruta_modelos = "modelos_calibrados.pkl"
    ruta_imputer = "imputer.pkl"
    ruta_nreg = "n_regimenes_backtest.txt"

    inconsistente = False

    if os.path.exists(ruta_nreg):
        with open(ruta_nreg, "r") as f:
            n_reg_hist = int(f.read().strip())
        if n_reg_hist != n_reg_opt:
            print(f"⚠️ Regímenes incompatibles: entrenado {n_reg_hist}, actual {n_reg_opt}")
            inconsistente = True
    else:
        print("⚠️ No se encontró archivo de n_regimenes. Asumo inconsistencia.")
        inconsistente = True

    if inconsistente:
        for ruta in [ruta_backtest, ruta_modelos, ruta_imputer, ruta_nreg]:
            if os.path.exists(ruta):
                os.remove(ruta)
                print(f"🗑️ Archivo eliminado: {ruta}")

        df_backtest_nuevo = entrenar_modelos_calibrados(df_modelo, features, n_regimenes=n_reg_opt)
        df_backtest_nuevo.to_csv(ruta_backtest, index=False)

        return df_backtest_nuevo
    else:
        print("✅ Regímenes consistentes. No se reinicia.")
        return pd.read_csv(ruta_backtest)
from datetime import datetime
from sklearn.experimental import enable_iterative_imputer  # debe ir antes
from sklearn.impute import IterativeImputer
import os
import pandas as pd

# === 0. Parámetros del modelo ===
n_reg_opt = 3
variables_opt = ['vol_tir_5d', 'spread_TIR_INF', 'SHOCK_CCL']
dias_entrenamiento = [0, 2]  # lunes y miércoles
dia_recomendacion = 4        # viernes
top_n = 5
BASE_PATH = "."  # o ruta absoluta si lo querés afuera

# === 1. Diccionarios de instrumentos ===
vencimientos, valores_finales, emisiones = get_info_lecaps(r"C:\Users\gaspar.carra\Desktop\LECAPs-Quant-Strategy\data\LECAPS DATOS.xlsx")

# === 2. Carga de datos ===
df_lecaps, futuros_data, df_badlar, df_rem, df_ccl, df_riesgo, df_brecha, fechas_licitaciones, fechas_canjes = load_data(
    path_lecaps, path_macro, path_futuros, vencimientos=vencimientos

)
df_rem = df_rem[["FECHA_PUBLICACION", "VALOR"]].rename(columns={"FECHA_PUBLICACION": "FECHA", "VALOR": "INFLACION_REM_ANUAL"})




# === 3. Dataset completo y modelo ===
# === 3. Dataset completo y modelo ===
df_lecaps_full, df_modelo, features = preparar_dataset(
    df_lecaps, futuros_data, df_badlar, df_rem, df_ccl, df_riesgo, df_brecha,
    fechas_licitaciones, fechas_canjes,
    vencimientos, valores_finales, emisiones,
    variables_hmm=variables_opt,
    n_regimenes=n_reg_opt
)

# === Enriquecimiento post dataset ===
df_lecaps_full = agregar_momentum_curva(df_lecaps_full)
df_lecaps_full = agregar_info_vencimientos(df_lecaps_full)
df_lecaps_full = agregar_score_manual(df_lecaps_full)
df_lecaps_full = agregar_dias_a_liquidacion(df_lecaps_full, fechas_licitaciones)

df_modelo = agregar_momentum_curva(df_modelo)
df_modelo = agregar_info_vencimientos(df_modelo)
df_modelo = agregar_score_manual(df_modelo)
df_modelo = agregar_dias_a_liquidacion(df_modelo, fechas_licitaciones)


from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def evaluar_dias_entrenamiento_pro(df_modelo, features, dias_train_lista, dias_op_lista, ventana=60, top_n=5):
    resultados = []

    fechas = sorted(df_modelo["FECHA"].unique())

    for dias_train in dias_train_lista:
        for dia_op in dias_op_lista:

            retornos_por_fecha = []

            for i in range(ventana, len(fechas)):
                fecha_actual = fechas[i]

                # Test solo si coincide día de operación
                if fecha_actual.dayofweek != dia_op:
                    continue

                # ventana rolling
                fechas_train = [f for f in fechas[i-ventana:i] if f.dayofweek in dias_train]
                if len(fechas_train) < 10:
                    continue

                df_train = df_modelo[df_modelo["FECHA"].isin(fechas_train)].dropna(subset=['ret_futuro_5d'] + features)
                df_test = df_modelo[df_modelo["FECHA"] == fecha_actual].dropna(subset=features)

                if df_train.empty or df_test.empty:
                    continue

                modelo = Pipeline([
                    ('scaler', StandardScaler()),
                    ('reg', Ridge(alpha=1.0))
                ])

                X_train = df_train[features]
                y_train = df_train["ret_futuro_5d"]
                modelo.fit(X_train, y_train)

                df_test = df_test.copy()
                df_test["ret_pred"] = modelo.predict(df_test[features])

                # top_n del día actual
                top_dia = df_test.sort_values("ret_pred", ascending=False).head(top_n)

                # retorno promedio del día
                retornos_por_fecha.append(top_dia["ret_futuro_5d"].mean())

            if len(retornos_por_fecha) == 0:
                continue

            resultados.append({
                "dias_train": dias_train,
                "dia_op": dia_op,
                "n_muestras": len(retornos_por_fecha),
                "ret_promedio": np.mean(retornos_por_fecha),
                "sharpe_aprox": np.mean(retornos_por_fecha) / np.std(retornos_por_fecha) if np.std(retornos_por_fecha) > 0 else np.nan
            })

    return pd.DataFrame(resultados).sort_values("ret_promedio", ascending=False)




# === 4. Validación o regeneración del backtest ===
df_backtest_hist = resetear_si_inconsistente(n_reg_opt, df_modelo, features)

resultados_evaluacion = evaluar_dias_entrenamiento(df_modelo, features)
resultados_evaluacion.head()


# 👉 Entrenar modelos si no existen
modelo_path = "modelos_finales.pkl"
imputer_path = "imputer.pkl"

if not os.path.exists(modelo_path) or not os.path.exists(imputer_path):
    print("🔁 Entrenando modelos de regresión y guardando imputador...")
    df_backtest_completo = entrenar_modelos_regresion(
        df_modelo,
        features,
        ventana=60,              # o el valor que estás usando
        n_regimenes=n_reg_opt    # asegurate de tener esto definido
    )
    print("✅ Modelos entrenados y guardados.")
else:
    print("✅ Modelos ya existen, se saltea entrenamiento.")

# === 5. Predicción y generación de backtest actualizado ===
df_backtest_completo = predecir_top_5_con_regimen_adaptativo(
    df=df_lecaps_full,
    features=features,
    top_n=top_n,
    df_backtest_hist=df_backtest_hist,
    ventana=60,
    path_csv=os.path.join(BASE_PATH, "backtest_lecaps.csv")
)

print("✅ Archivo generado:", os.path.exists(os.path.join(BASE_PATH, "backtest_lecaps.csv")))

