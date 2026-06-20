#!/usr/bin/env python3
"""Generate charts for PETRONAS Dossier — PNG output at 300 DPI for print PDF."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUT = '/root/arifOS/forge_work/PETRONAS_DOSSIER/assets'

# Palette
MERAH = '#CC0000'
EMAS = '#D4A847'
HITAM = '#1A1A1A'
PUTIH = '#F5F0E8'
MERAH_MUDA = '#FFE0E0'
HIJAU = '#1A6B3C'
KELABU = '#888888'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.edgecolor': '#DDD',
    'axes.grid': True,
    'grid.alpha': 0.3,
})
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Segoe UI', 'Arial']

def chart1_profit_drop():
    """Bar chart: Profit drop 45.8%"""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    years = ['FY2022', 'FY2023', 'FY2024']
    values = [101.6, 80.7, 55.1]
    colors = [EMAS, '#C4A030', MERAH]

    bars = ax.bar(years, values, color=colors, width=0.55, edgecolor='none', zorder=3)
    
    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f'RM{val:.1f}B', ha='center', va='bottom', fontsize=14, fontweight='bold', color=HITAM)

    # Add drop arrows
    ax.annotate('', xy=(0.7, 80), xytext=(0.7, 95),
                arrowprops=dict(arrowstyle='->', color=MERAH, lw=2))
    ax.text(0.7, 76, '-20.6%', ha='center', fontsize=10, color=MERAH, fontweight='bold')

    ax.annotate('', xy=(1.7, 55), xytext=(1.7, 75),
                arrowprops=dict(arrowstyle='->', color=MERAH, lw=2))
    ax.text(1.7, 51, '-31.7%', ha='center', fontsize=10, color=MERAH, fontweight='bold')

    ax.set_ylabel('Profit After Tax (RM Billion)', fontsize=10, color=KELABU)
    ax.set_ylim(0, 125)
    ax.set_title('PETRONAS Profit Collapse Under TT', fontsize=16, fontweight='bold', color=HITAM, pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors=KELABU, labelsize=10)

    # Total drop annotation
    ax.annotate('Total: -45.8%', xy=(1.3, 108), fontsize=12, fontweight='bold',
                color=MERAH, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=MERAH_MUDA, edgecolor=MERAH, alpha=0.9))

    plt.tight_layout()
    path = os.path.join(OUT, 'chart1_profit_drop.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Chart 1: {path}')
    return path

def chart2_f1_vs_workers():
    """F1 RM340M vs worker cost visualization"""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    categories = ['F1 Sponsorship\n(per year)', 'Avg Worker Cost\n(per year)']
    values = [340, 0.150]  # RM340M vs RM150K
    colors = [MERAH, HIJAU]

    bars = ax.barh(categories, values, color=colors, height=0.45, edgecolor='none', zorder=3)

    for bar, val in zip(bars, values):
        label = 'RM340,000,000' if val > 1 else 'RM150,000'
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                label, ha='left', va='center', fontsize=12, fontweight='bold', color=HITAM)

    ax.set_xlim(0, 420)
    ax.set_title('Where The Money Goes', fontsize=16, fontweight='bold', color=HITAM, pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors=KELABU, labelsize=11)
    ax.set_xlabel('RM Million', fontsize=10, color=KELABU)

    # Ratio annotation
    ax.annotate('1 F1 = 2,267 workers', xy=(200, -0.35), fontsize=13, fontweight='bold',
                color=MERAH, ha='center',
                bbox=dict(boxstyle='round,pad=0.4', facecolor=MERAH_MUDA, edgecolor=MERAH, alpha=0.9))

    plt.tight_layout()
    path = os.path.join(OUT, 'chart2_f1_vs_workers.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Chart 2: {path}')
    return path

def chart3_math_maruah():
    """F1 math: how many workers could be saved"""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Bar: workers fired vs workers F1 could save
    labels = ['Workers\nFIRED', 'Workers F1\nCould Save', 'Difference\n(Shame Gap)']
    values = [5000, 2267, 2733]
    colors = [MERAH, HIJAU, KELABU]

    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='none', zorder=3)

    for bar, val in zip(bars, values):
        label = f'{val:,}' if val else ''
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
                label, ha='center', va='bottom', fontsize=14, fontweight='bold', color=HITAM)

    ax.set_ylim(0, 6000)
    ax.set_title('The Mathematics of Maruah', fontsize=16, fontweight='bold', color=HITAM, pad=12)
    ax.set_ylabel('Number of Workers', fontsize=10, color=KELABU)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors=KELABU, labelsize=10)

    plt.tight_layout()
    path = os.path.join(OUT, 'chart3_math_maruah.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Chart 3: {path}')
    return path

if __name__ == '__main__':
    chart1_profit_drop()
    chart2_f1_vs_workers()
    chart3_math_maruah()
    print('All charts generated.')
