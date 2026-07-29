# ui/styles.py — Estilos CSS globais
import streamlit as st

def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(ellipse at 50% 0%, #1a1a2e 0%, #0e1117 50%, #000000 100%); background-attachment: fixed; }

        .main-title { font-size: 2.8rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #ffd700, #ffaa00, #ffd700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; }
        .subtitle { text-align: center; color: #b0b0b0; font-size: 0.9rem; margin-bottom: 1.5rem; letter-spacing: 2px; }
        .gold-highlight { font-size: 2rem; font-weight: 900; background: linear-gradient(135deg, #ffd700, #ffaa00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block; text-align: center; margin-bottom: 12px; }

        .divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,215,0,0.2), transparent); margin: 24px 0; }

        .stButton > button {
            background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; border: none;
            font-weight: 700; font-size: 1rem; border-radius: 12px; padding: 12px 24px;
            letter-spacing: 1px; box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 8px 25px rgba(255,215,0,0.5); }

        .team-block {
            border-radius: 16px; padding: 18px 14px; margin-bottom: 20px;
        }
        .team-block.home { background: linear-gradient(145deg, rgba(255,215,0,0.08), rgba(255,215,0,0.02)); border: 1px solid rgba(255,215,0,0.3); }
        .team-block.away { background: linear-gradient(145deg, rgba(192,192,192,0.08), rgba(192,192,192,0.02)); border: 1px solid rgba(192,192,192,0.3); }
        .team-title { font-size: 1.4rem; font-weight: 800; text-align: center; margin-bottom: 16px; }
        .team-title.home-title { color: #ffd700; }
        .team-title.away-title { color: #c0c0c0; }

        .section-title {
            font-size: 1.6rem; font-weight: 800; text-align: center;
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 32px 0 16px 0;
        }
        .dimension-title { font-size: 1.1rem; font-weight: 700; color: #ffd700; margin: 12px 0 8px 0; padding-left: 8px; border-left: 3px solid #ffd700; }

        .mpv-hero {
            background: radial-gradient(circle at 50% 0%, rgba(255,215,0,0.18) 0%, transparent 75%);
            border: 2px solid #ffd700;
            border-radius: 32px;
            padding: 28px 16px;
            text-align: center;
            margin: 24px 0;
            animation: heroGlow 2s ease-in-out infinite alternate;
        }
        @keyframes heroGlow {
            from { box-shadow: 0 0 25px rgba(255,215,0,0.25); }
            to { box-shadow: 0 0 50px rgba(255,215,0,0.6), 0 0 100px rgba(255,140,0,0.3); }
        }
        .mpv-crown { font-size: 3rem; margin-bottom: 8px; }
        .mpv-main-values { display: flex; justify-content: center; align-items: center; gap: 24px; }
        .mpv-value { font-size: 5rem; font-weight: 900; line-height: 1; }
        .mpv-value.home-value { background: linear-gradient(180deg, #ffd700 0%, #ff8c00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .mpv-value.away-value { background: linear-gradient(180deg, #c0c0c0 0%, #a0a0a0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .mpv-vs { font-size: 1.8rem; color: #888; font-weight: 700; }
        .mpv-bar {
            height: 8px; background: #333; border-radius: 4px; margin: 16px 0 8px; overflow: hidden;
            display: flex;
        }
        .mpv-bar-fill { height: 100%; background: linear-gradient(90deg, #ffd700, #ff8c00); }
        .mpv-bar-fill.away { background: linear-gradient(90deg, #c0c0c0, #a0a0a0); }

        .comp-card {
            background: rgba(20,20,35,0.9); border-radius: 16px; padding: 16px;
            border: 1px solid rgba(255,215,0,0.25); text-align: center;
        }
        .comp-card h4 { color: #ffd700; margin-bottom: 8px; }
        .comp-card .big { font-size: 2rem; font-weight: 900; }
        .comp-card .small { font-size: 0.8rem; color: #aaa; }

        .detail-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
        .detail-table th { color: #ffd700; font-weight: 600; padding: 8px; border-bottom: 1px solid #333; text-align: left; }
        .detail-table td { padding: 8px; border-bottom: 1px solid #222; color: #ddd; }
        .team-block.gold-highlight {
    border: 2px solid #ffd700 !important;
    box-shadow: 0 0 20px rgba(255,215,0,0.4);
}
.team-block.gold-highlight .team-title {
    font-size: 1.6rem;
    text-shadow: 0 0 10px rgba(255,215,0,0.5);
}
    </style>
    """, unsafe_allow_html=True)
