import numpy as np
import matplotlib.pyplot as plt

# 图1：IEEE-118 真实数据
def fig1():
    loads = [30, 31, 32, 39, 40]
    baseline = [0.067, 0.133, 0.167, 0.570, 0.588]
    controlled = [0.067, 0.133, 0.167, 0.476, 0.491]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,4))
    ax1.plot(loads, baseline, 'o-', label='Baseline', color='red')
    ax1.plot(loads, controlled, 's-', label='Controlled', color='blue')
    ax1.axvspan(30, 50, alpha=0.2, color='gray')
    ax1.set_xlabel('Load (MW)'); ax1.set_ylabel('Collapse probability')
    ax1.set_title('IEEE-118'); ax1.legend(); ax1.grid(True)
    
    cats = ['Baseline', 'With memory', 'No memory']
    vals = [0.588, 0.491, 0.588]
    ax2.bar(cats, vals, color=['red','blue','gray'])
    ax2.set_ylabel('Collapse probability at 40 MW')
    ax2.set_title('Memory ablation')
    ax2.set_ylim(0,0.7)
    ax2.text(0, 0.55, 'Δ=0.096', ha='center', color='blue')
    ax2.text(2, 0.55, 'Δ=0', ha='center', color='gray')
    plt.tight_layout()
    plt.savefig('fig1_true.png', dpi=300); plt.close()
    print('fig1_true.png saved')

# 图2：跨系统 Δ
def fig2():
    systems = ['IEEE-39', 'IEEE-118', 'IEEE-300', 'IEEE-2383']
    delta = [0.68, 0.096, 0.332, 1.0]
    plt.figure(figsize=(6,5))
    bars = plt.bar(systems, delta, color=['green','orange','blue','red'])
    plt.ylabel('Peak Δ'); plt.title('Cross-system comparison')
    plt.ylim(0,1.2)
    for bar,d in zip(bars, delta):
        plt.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.03, f'{d:.3f}', ha='center')
    plt.text(3, 1.05, '* Only at transition point', ha='center', style='italic')
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig('fig2_true.png', dpi=300); plt.close()
    print('fig2_true.png saved')

# 图3：IEEE-300 真实数据（手动填入）
def fig3():
    loads = [115, 120, 122, 124, 125, 126, 128, 130]
    baseline = [0.476, 0.552, 0.580, 0.608, 0.620, 0.628, 0.636, 0.640]
    controlled = [0.296, 0.296, 0.296, 0.296, 0.296, 0.296, 0.328, 0.484]
    delta = np.array(baseline) - np.array(controlled)
    
    fig, ax1 = plt.subplots(figsize=(8,5))
    ax1.plot(loads, baseline, 'o-', color='red', label='Baseline')
    ax1.plot(loads, controlled, 's-', color='blue', label='Controlled')
    ax1.set_xlabel('Load (MW)'); ax1.set_ylabel('Collapse probability')
    ax1.legend(loc='upper left'); ax1.grid(True, linestyle='--')
    ax1.axvspan(115, 130, alpha=0.15, color='gray', label='Critical band')
    
    ax2 = ax1.twinx()
    ax2.plot(loads, delta, 'd-', color='green', linewidth=2, label='Δ')
    idx = np.argmax(delta)
    ax2.plot(loads[idx], delta[idx], 'D', color='darkgreen', markersize=8)
    ax2.annotate(f'Peak Δ = {delta[idx]:.3f}', xy=(loads[idx], delta[idx]),
                 xytext=(loads[idx]+1, delta[idx]+0.05),
                 arrowprops=dict(arrowstyle='->', color='darkgreen'))
    ax2.set_ylabel('Suppression Δ', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    
    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, lab1+lab2, loc='upper right')
    ax1.set_title('IEEE-300: Finite-width critical band')
    plt.tight_layout()
    plt.savefig('fig3_true.png', dpi=300); plt.close()
    print('fig3_true.png saved')

if __name__ == '__main__':
    fig1()
    fig2()
    fig3()
    print('All true figures generated. Please open fig3_true.png and verify the numbers.')