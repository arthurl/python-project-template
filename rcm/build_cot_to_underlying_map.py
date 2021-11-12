"""Clean up tickers_full.csv data"""
# pylint: disable=unused-import, missing-function-docstring

import re

import pandas as pd
import numpy as np


tickers_full: pd.DataFrame = pd.read_csv(
    r"c:/src/cotdatafetcher/test_data/tickers_full.original.csv"
)

tickers_full["Ticker"] = tickers_full["Ticker"].map(
    lambda x: re.sub(r"([0-9A-Z]{8}) Index", r"\1", x.strip()), na_action="ignore"
)

metric_map = {
    '("Open Interest")': "Open interest",
    '("Number of Traders")': "Number of traders",
    "(Volume)": "Volume",
    '("Number of Positions")': "Number of positions",
    '("Percentage of Open Interest")': "Percent OI",
}

tickers_full["Metric"] = tickers_full["Metric"].map(metric_map, na_action="ignore")

tradertype_map = {
    # CFTC Disaggregated
    "(Producer/Merchant/Processor/User)": "Producer",
    '("Swap Dealers")': "Swap Dealers",
    '("Managed Money")': "Managed Money",
    '("Other Reportables")': "Other Reportables",
    # CFTC Legacy
    "(Commercial)": "Commercial",
    "(Non-Commercial)": "Non-Commercial",
    # MiFID
    '("Investment Firms or Credit Institutions")': "Investment Firms or Credit Institutions",
    '("Investment Funds")': "Investment Funds",
    '("Other Financial Institutions")': "Other Financial Institutions",
    '("Commercial Undertakings")': "Commercial Undertakings",
    '("Directive Compliance Obligations")': "Directive Compliance Obligations",
    # ??
    "()": "",
    '("Index Traders")': "",
    '("Top 20 Members")': "",
    '("Non-Futures Firm (non-FFmember)")': "",
    '("Futures Firm (FFmember)")': "",
}

underlying_map = {'("AADH22 Comdty")': "AAD", '("AAWQ24 Comdty")': "AAW", '("AAX1 Comdty")': "AA", '("ABEN22 Comdty")': "ABE", '("ACTX24 Comdty")': "ACT", '("ADM6 Curncy")': np.nan, '("AEBU23 Comdty")': "AEB", '("AEDQ23 Comdty")': "AED", '("AEOZ21 Comdty")': "AEO", '("AFYK22 Comdty")': "AFY", '("AGDG22 Comdty")': "AGD", '("AGOG22 Comdty")': "AGO", '("AGX6 Comdty")': "AG", '("AHBV21 Comdty")': "AHB", '("AIRV22 Comdty")': "AIR", '("AJDX21 Comdty")': "AJD", '("AJIM23 Comdty")': "AJI", '("AJPN22 Comdty")': "AJP", '("AJYMAY1 Comdty")': "AJY", '("AKYK23 Comdty")': "AKY", '("ALOG22 Comdty")': "ALO", '("ALYQ22 Comdty")': "ALY", '("AMEF22 Comdty")': "AME", '("AMTX21 Comdty")': "AMT", '("AMYZ21 Comdty")': "AMY", '("ANDH23 Comdty")': "AND", '("ANPN24 Comdty")': "ANP", '("AOAV24 Comdty")': "AOA", '("AOEN22 Comdty")': "AOE", '("APM29 Comdty")': "AP", '("APTF22 Comdty")': "APT", '("AQPZ21 Comdty")': "AQP", '("ARAX22 Comdty")': "ARA", '("ASD1 Comdty")': np.nan, '("ASIX21 Comdty")': "ASI", '("ASOQ23 Comdty")': "ASO", '("AUA6 Comdty")': np.nan, '("AUPF6 Comdty")': "AUP", '("AVRH25 Comdty")': "AVR", '("AYYU22 Comdty")': "AYY", '("AZBH22 Comdty")': "AZB", '("BAPG3 Comdty")': "BAP", '("BHQ7 Comdty")': "BH", '("BITH3 Comdty")': "BIT", '("BL3 Index")': np.nan, '("BOZ1 Comdty")': "BO", '("BPU5 Curncy")': np.nan, '("BR58 Curncy")': np.nan, '("BSDZ21 Comdty")': "BSD", '("BSROCT1 Comdty")': "BSR", '("BSYMAR1 Comdty")': "BSY", '("BTCQ1 Curncy")': np.nan, '("BVW60 Comdty")': np.nan, '("BWCJUN1 Comdty")': "BWC", '("BWW23 Comdty")': np.nan, '("BXINOV1 Comdty")': "BXI", '("BXT16 Comdty")': np.nan, '("BYB125 Comdty")': np.nan, '("BZAU6 Comdty")': "BZA", '("BZP5 Comdty")': np.nan, '("C Z4 Comdty")': np.nan, '("CAAH23 Comdty")': "CAA", '("CAEH22 Comdty")': "CAE", '("CAK4 Comdty")': "CA", '("CAPM2 Comdty")': "CAP", '("CAR13 Comdty")': np.nan, '("CBEM24 Comdty")': "CBE", '("CBO29 Comdty")': np.nan, '("CBYK22 Comdty")': "CBY", '("CCN3 Comdty")': "CC", '("CCOV22 Comdty")': "CCO", '("CCWJ22 Comdty")': "CCW", '("CCYK23 Comdty")': "CCY", '("CD8 Curncy")': np.nan, '("CDRK22 Comdty")': "CDR", '("CFI7 Comdty")': np.nan, '("CFPU1 Comdty")': "CFP", '("CGYAUG1 Comdty")': "CGY", '("CHEN3 Comdty")': "CHE", '("CHLH4 Comdty")': "CHL", '("CIDJAN1 Comdty")': "CID", '("CJIF25 Comdty")': "CJI", '("CJPX23 Comdty")': "CJP", '("CLV7 Comdty")': "CL", '("CLYF22 Comdty")': "CLY", '("CNP2 Comdty")': np.nan, '("COZ5 Comdty")': "CO", '("CRWQ22 Comdty")': "CRW", '("CTK3 Comdty")': "CT", '("CUAJ4 Comdty")': "CUA", '("CUK2 Comdty")': "CU", '("CWBJ23 Comdty")': "CWB", '("CXTJAN1 Comdty")': "CXT", '("CYIV25 Comdty")': "CYI", '("CYLM23 Comdty")': "CYL", '("CYRX21 Comdty")': "CYR", '("DAEV5 Comdty")': "DAE", '("DAH2 Comdty")': "DA", '("DEWU22 Comdty")': "DEW", '("DFNOV2 Comdty")': "DF", '("DGOQ23 Comdty")': "DGO", '("DI3 Comdty")': np.nan, '("DJ19 Comdty")': "D", '("DJ3 Index")': np.nan, '("DJCF22 Comdty")': "DJC", '("DLQ2 Comdty")': "DL", '("DMAPR2 Comdty")': "DM", '("DMH2 Index")': np.nan, '("DNZ5 Index")': np.nan, '("DS1 Comdty")': np.nan, '("DX3 Curncy")': np.nan, '("EC9 Curncy")': np.nan, '("ECZ5 Comdty")': "EC", '("EDZ4 Comdty")': "ED", '("EMX1 Comdty")': "EM", '("ENV6 Comdty")': "EN", '("EOM4 Comdty")': "EO", '("EPQ2 Comdty")': "EP", '("ESU1 Index")': np.nan, '("FAZ1 Index")': np.nan, '("FCSEP2 Comdty")': "FC", '("FFZ5 Comdty")': "FF", '("FOG2 Comdty")': "FO", '("FVH2 Comdty")': "FV", '("GC15 Comdty")': np.nan, '("GIU1 Index")': np.nan, '("GSM2 Comdty")': "GS", '("HGN3 Comdty")': "HG", '("HOF4 Comdty")': "HO", '("HRCZ1 Comdty")': "HRC", '("HU3 Comdty")': "H", '("HUP11 Comdty")': np.nan, '("I036 Comdty")': np.nan, '("I658 Comdty")': np.nan, '("IAQ3 Comdty")': "IA", '("IEZ6 Comdty")': "IE", '("IHDV3 Comdty")': "IHD", '("IHOZ5 Comdty")': "IHO", '("II7 Comdty")': np.nan, '("IJX2 Comdty")': "IJ", '("IKBQ3 Comdty")': "IKB", '("ILOQ4 Comdty")': "ILO", '("ILPK6 Comdty")': "ILP", '("INIX22 Comdty")': "INI", '("IOK3 Comdty")': "IO", '("IWZ30 Comdty")': "IW", '("IXAM2 Index")': np.nan, '("IXP3 Index")': np.nan, '("IXRM2 Index")': np.nan, '("IXS4 Index")': np.nan, '("JAAH4 Comdty")': "JAA", '("JCOV4 Comdty")': "JCO", '("JCWX23 Comdty")': "JCW", '("JOX0 Comdty")': "JO", '("JOX1 Comdty")': "JO", '("JWEF22 Comdty")': "JWE", '("JY1 Curncy")': np.nan, '("KCZ3 Comdty")': "KC", '("KSPF2 Comdty")': "KSP", '("KVMAR1 Comdty")': "KV", '("KWU2 Comdty")': "KW", '("LAK29 Comdty")': "LA", '("LBJAN2 Comdty")': "LB", '("LCAPR2 Comdty")': "LC", '("LCO14 Comdty")': np.nan, '("LEH2 Comdty")': "LE", '("LHAPR1 Comdty")': "LH", '("LKH3 Comdty")': "LK", '("LLG2 Comdty")': "LL", '("LNQ3 Comdty")': "LN", '("LP99 Comdty")': np.nan, '("LQAZ5 Comdty")': "LQA", '("LRN3 Comdty")': "LR", '("LTX2 Comdty")': "LT", '("LWAX2 Comdty")': "LWA", '("LWH5 Comdty")': "LW", '("LXN4 Comdty")': "LX", '("LYM3 Comdty")': "LY", '("MD5 Index")': np.nan, '("MESZ3 Index")': np.nan, '("MFSZ1 Index")': np.nan, '("MMBU2 Comdty")': "MMB", '("MNCG3 Comdty")': "MNC", '("MOZ26 Comdty")': "MO", '("MPYV1 Comdty")': "MPY", '("MWU1 Comdty")': "MW", '("MY5 Comdty")': np.nan, '("ND1 Index")': np.nan, '("NDN30 Comdty")': "ND", '("NGF30 Comdty")': "NG", '("NH16 Index")': np.nan, '("NQH2 Index")': np.nan, '("NRG30 Comdty")': "NR", '("NSH3 Comdty")': "NS", '("NV3 Curncy")': np.nan, '("NXZ1 Index")': np.nan, '("O 10 Comdty")': np.nan, '("OOPF3 Comdty")': "OOP", '("PAU2 Comdty")': "PA", '("PB5 Comdty")': np.nan, '("PBL1 Comdty")': np.nan, '("PE5 Curncy")': np.nan, '("PI11 Comdty")': np.nan, '("PJBK6 Comdty")': "PJB", '("PJPX2 Comdty")': "PJP", '("PL4 Comdty")': np.nan, '("PSEX3 Comdty")': "PSE", '("PWOF6 Comdty")': "PWO", '("PXX1 Comdty")': "PX", '("QB60 Comdty")': np.nan, '("QCK3 Comdty")': "QC", '("QGR13 Comdty")': np.nan, '("QJBH22 Comdty")': "QJB", '("QK10 Comdty")': "Q", '("QSM5 Comdty")': "QS", '("QWMAR1 Comdty")': "QW", '("QZ27 Comdty")': "Q", '("QZTJ3 Comdty")': "QZT", '("R6Q4 Comdty")': np.nan, '("RAK2 Curncy")': np.nan, '("RBTMAY1 Comdty")': "RBT", '("REG4 Comdty")': "RE", '("RGPM22 Comdty")': "RGP", '("RJI2 Comdty")': np.nan, '("RJV2 Comdty")': "RJ", '("RL3 Index")': np.nan, '("RNX5 Comdty")': "RN", '("ROCF2 Comdty")': "ROC", '("RP4 Curncy")': np.nan, '("RRH2 Comdty")': "RR", '("RSF3 Comdty")': "RS", '("RTA1 Index")': np.nan, '("RTJ2 Comdty")': "RT", '("RTY3 Index")': np.nan, '("RUK2 Curncy")': np.nan, '("RVDK2 Comdty")': "RVD", '("RXEN24 Comdty")': "RXE", '("S X1 Comdty")': np.nan, '("SAIQ2 Comdty")': "SAI", '("SBK3 Comdty")': "SB", '("SDEU22 Comdty")': "SDE", '("SDL13 Comdty")': np.nan, '("SERG2 Comdty")': "SER", '("SFIM2 Comdty")': "SFI", '("SFM2 Curncy")': np.nan, '("SFRU3 Comdty")': "SFR", '("SIN6 Comdty")': "SI", '("SMOJ22 Comdty")': "SMO", '("SMZ4 Comdty")': "SM", '("SP2 Index")': np.nan, '("TIOM3 Comdty")': "TIO", '("TJJUN1 Comdty")': "TJ", '("TK2 Comdty")': "T", '("TNMAR1 Comdty")': "TN", '("TOG4 Comdty")': "TO", '("TTAX1 Comdty")': "TTA", '("TUZ1 Comdty")': "TU", '("TYDEC1 Comdty")': "TY", '("UDSH3 Comdty")': "UDS", '("UE65 Comdty")': np.nan, '("UFX1 Comdty")': "UF", '("UJLZ6 Comdty")': "UJL", '("UMJAN3 Comdty")': "UM", '("UNU4 Comdty")': "UN", '("UO60 Comdty")': np.nan, '("UP53 Comdty")': np.nan, '("UQM2 Comdty")': "UQ", '("USU1 Comdty")': "US", '("UTU4 Comdty")': "UT", '("UU34 Comdty")': "U", '("UXH2 Index")': np.nan, '("UXYZ1 Comdty")': "UXY", '("V6SEP1 Comdty")': "V6", '("VCZ1 Comdty")': "VC", '("VHG5 Comdty")': "VH", '("VKDJ23 Comdty")': "VKD", '("VRAH3 Comdty")': "VRA", '("W 6 Comdty")': np.nan, '("W6V2 Comdty")': np.nan, '("W7H4 Comdty")': np.nan, '("W9G3 Comdty")': np.nan, '("WATJUN1 Comdty")': "WAT", '("WAYX24 Comdty")': "WAY", '("WBSJ2 Comdty")': "WBS", '("WEK3 Comdty")': "WE", '("WNU1 Comdty")': "WN", '("WP21 Comdty")': np.nan, '("WRTN2 Comdty")': "WRT", '("WS25 Comdty")': np.nan, '("WTG3 Comdty")': "WT", '("WUV2 Comdty")': "WU", '("WYIQ2 Comdty")': "WYI", '("XBT2 Curncy")': np.nan, '("XBV1 Comdty")': "XB", '("XII8 Comdty")': np.nan, '("XOOZ1 Comdty")': "XOO", '("YBU4 Comdty")': "YB", '("YKQ3 Comdty")': "YK", '("YQ71 Comdty")': "Y", '("YSSZ24 Comdty")': "YSS", '("YTLG24 Comdty")': "YTL", '("YTRU27 Comdty")': "YTR", '("YTS28 Comdty")': np.nan, '("YTTF23 Comdty")': "YTT", '("YUTM25 Comdty")': "YUT", '("YUW11 Comdty")': np.nan, '("YUYV29 Comdty")': "YUY", '("YVB6 Comdty")': np.nan, '("YVCV21 Comdty")': "YVC", '("YVMAY3 Comdty")': "YV", '("YVOG28 Comdty")': "YVO", '("YVYV28 Comdty")': "YVY", '("YX25 Comdty")': "Y", '("YZBU26 Comdty")': "YZB", '("YZCK26 Comdty")': "YZC", '("YZEU23 Comdty")': "YZE", '("YZIH26 Comdty")': "YZI", '("YZSQ29 Comdty")': "YZS", '("YZTU24 Comdty")': "YZT", '("Z0Q4 Comdty")': np.nan, '("ZAAU26 Comdty")': "ZAA", '("ZASZ31 Comdty")': "ZAS", '("ZATU25 Comdty")': "ZAT", '("ZAV4 Comdty")': "ZA", '("ZAYU25 Comdty")': "ZAY", '("ZBBJ30 Comdty")': "ZBB", '("ZBEX27 Comdty")': "ZBE", '("ZBIX24 Comdty")': "ZBI", '("ZBON27 Comdty")': "ZBO", '("ZCAZ26 Comdty")': "ZCA", '("ZDAPR3 Comdty")': "ZD", '("ZDBF26 Comdty")': "ZDB", '("ZDCH25 Comdty")': "ZDC", '("ZDDX26 Comdty")': "ZDD", '("ZDEU26 Comdty")': "ZDE", '("ZDIZ23 Comdty")': "ZDI", '("ZDOX27 Comdty")': "ZDO", '("ZDRQ25 Comdty")': "ZDR", '("ZEA103 Comdty")': np.nan, '("ZECV31 Comdty")': "ZEC", '("ZFIF28 Comdty")': "ZFI", '("ZFLG31 Comdty")': "ZFL", '("ZFOU30 Comdty")': "ZFO", '("ZFYF26 Comdty")': "ZFY", '("ZG2 Comdty")': "Z", '("ZGDV23 Comdty")': "ZGD", '("ZHEG22 Comdty")': "ZHE", '("ZHTZ27 Comdty")': "ZHT", '("ZIAU29 Comdty")': "ZIA", '("ZIBM22 Comdty")': "ZIB", '("ZIEX22 Comdty")': "ZIE", '("ZIIZ27 Comdty")': "ZII", '("ZIYX27 Comdty")': "ZIY", '("ZJ30 Comdty")': "Z", '("ZJBM27 Comdty")': "ZJB", '("ZJDFEB1 Comdty")': "ZJD", '("ZJLU25 Comdty")': "ZJL", '("ZJWM24 Comdty")': "ZJW", '("ZK60 Comdty")': "Z", '("ZKDJ27 Comdty")': "ZKD", '("ZKIU30 Comdty")': "ZKI", '("ZKOZ22 Comdty")': "ZKO", '("ZLLX27 Comdty")': "ZLL", '("ZLRM24 Comdty")': "ZLR", '("ZLSK26 Comdty")': "ZLS", '("ZM34 Comdty")': "Z", '("ZMIG27 Comdty")': "ZMI", '("ZMPN31 Comdty")': "ZMP", '("ZNAX1 Comdty")': "ZNA", '("ZOEJ24 Comdty")': "ZOE", '("ZONOV2 Comdty")': "ZO", '("ZOYX27 Comdty")': "ZOY", '("ZPV1 Comdty")': "ZP", '("ZQIU25 Comdty")': "ZQI", '("ZSDK26 Comdty")': "ZSD", '("ZU4 Comdty")': "Z", '("ZWH3 Comdty")': "ZW", '("ZWTJ24 Comdty")': "ZWT", '("ZXIX23 Comdty")': "ZXI", '("ZXWN26 Comdty")': "ZXW", '("ZXYV24 Comdty")': "ZXY", '("ZYEK23 Comdty")': "ZYE", '("ZYLQ24 Comdty")': "ZYL", '("ZZCK23 Comdty")': "ZZC", '("ZZDZ23 Comdty")': "ZZD", '("ZZIG25 Comdty")': "ZZI", '("ZZLQ23 Comdty")': "ZZL", '("ZZON25 Comdty")': "ZZO", '("ZZRN25 Comdty")': "ZZR", '("ZZSJ28 Comdty")': "ZZS", '("ZZTF30 Comdty")': "ZZT"}

tickers_full["Underlying"] = tickers_full["Underlying"].map(
    underlying_map, na_action="ignore"
)

ticker_to_underlying_map = (
    tickers_full[["Ticker", "Underlying"]]
    .dropna(subset=["Underlying"])
    .set_index("Ticker")
)

ticker_to_underlying_map.to_csv("underlyings.csv")
