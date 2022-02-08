import pandas as pd


def to_csv(data, out_dir):
    df = pd.DataFrame(data, columns=['ASIGURATOR', "NUMAR POLITA", "CLASA B/M", "DATA EMITERE", "DATA EXPIRARE",
                                     "NUME CLIENT", "NUMAR DE TELEFON", "TIP ASIGURARE", "NUMAR INMATRICULARE",
                                     "PERIODA DE ASIGURARE", "VALOARE POLITA", "POLITA PDF"])
    df["DATA EMITERE"] = df["DATA EMITERE"].astype("M8")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].astype("M8")
    df["DATA EMITERE"] = df["DATA EMITERE"].dt.strftime("%d.%m.%y")
    df["DATA EXPIRARE"] = df["DATA EXPIRARE"].dt.strftime("%d.%m.%y")
    df = df.sort_values(by=['NUME CLIENT'], ignore_index=True)
    df.to_csv(str(out_dir / 'db.csv'), index_label='NR.CRT', encoding='utf-8')