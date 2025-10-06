import matplotlib.pyplot as plt
import numpy as np

# Create figure with multiple subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('AI GPU Performance Comparison 2025-2026', fontsize=16, fontweight='bold')

# 1. Market Share
companies = ['NVIDIA', 'AMD', 'Intel', 'Others\n(Cerebras,\nGroq, etc)']
market_share = [90, 8, 1, 1]
colors = ['#76B900', '#ED1C24', '#0071C5', '#888888']

ax1.pie(market_share, labels=companies, autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('AI Accelerator Market Share 2025', fontsize=12, fontweight='bold')

# 2. Training Performance (Petaflops FP8)
products = ['NVIDIA\nBlackwell\nGB300', 'NVIDIA\nH200', 'AMD\nMI325X', 'AMD\nMI350\n(2025)', 'AMD\nMI400\n(2026)', 'Intel\nGaudi 3']
training_perf = [360, 280, 270, 350, 500, 150]  # Estimated petaflops
colors_bar = ['#76B900', '#76B900', '#ED1C24', '#ED1C24', '#ED1C24', '#0071C5']

bars1 = ax2.bar(range(len(products)), training_perf, color=colors_bar, alpha=0.8)
ax2.set_xticks(range(len(products)))
ax2.set_xticklabels(products, rotation=0, ha='center', fontsize=9)
ax2.set_ylabel('Training Performance (Petaflops FP8)', fontsize=10)
ax2.set_title('AI Training Performance Comparison', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars1, training_perf)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
             f'{val}', ha='center', va='bottom', fontsize=9)

# 3. Inference Performance (Relative to NVIDIA H200 = 100)
products_inf = ['NVIDIA\nBlackwell', 'NVIDIA\nH200', 'AMD\nMI325X', 'AMD\nMI350', 'Intel\nGaudi 3', 'Groq\nLPU', 'Cerebras\nWSE']
inference_perf = [130, 100, 95, 110, 85, 120, 115]  # Relative performance
colors_inf = ['#76B900', '#76B900', '#ED1C24', '#ED1C24', '#0071C5', '#FF6B35', '#4ECDC4']

bars2 = ax3.barh(range(len(products_inf)), inference_perf, color=colors_inf, alpha=0.8)
ax3.set_yticks(range(len(products_inf)))
ax3.set_yticklabels(products_inf, fontsize=9)
ax3.set_xlabel('Relative Inference Performance (H200 = 100)', fontsize=10)
ax3.set_title('AI Inference Performance Comparison', fontsize=12, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)

# Add value labels on bars
for bar, val in zip(bars2, inference_perf):
    ax3.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
             f'{val}', ha='left', va='center', fontsize=9)

# 4. Performance Roadmap Timeline
timeline_years = ['2024\nQ4', '2025\nQ1', '2025\nQ2', '2025\nQ3', '2025\nQ4', '2026\nQ1', '2026\nQ2', '2026\nQ3', '2026\nQ4']
nvidia_roadmap = [280, 280, 320, 360, 360, 380, 450, 450, 500]
amd_roadmap = [270, 270, 300, 350, 350, 400, 450, 500, 500]
intel_roadmap = [150, 150, 150, 180, 180, 200, 220, 220, 240]

ax4.plot(timeline_years, nvidia_roadmap, marker='o', linewidth=2.5, markersize=8,
         label='NVIDIA', color='#76B900')
ax4.plot(timeline_years, amd_roadmap, marker='s', linewidth=2.5, markersize=8,
         label='AMD', color='#ED1C24')
ax4.plot(timeline_years, intel_roadmap, marker='^', linewidth=2.5, markersize=8,
         label='Intel', color='#0071C5')

ax4.set_xlabel('Timeline', fontsize=10)
ax4.set_ylabel('Estimated Performance (Petaflops)', fontsize=10)
ax4.set_title('AI GPU Performance Roadmap 2024-2026', fontsize=12, fontweight='bold')
ax4.legend(loc='upper left', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.tick_params(axis='x', rotation=45)

# Annotations for key releases
ax4.annotate('GB300 NVL72', xy=(3, 360), xytext=(3, 410),
            arrowprops=dict(arrowstyle='->', color='#76B900', lw=1.5),
            fontsize=8, ha='center')
ax4.annotate('MI350', xy=(3, 350), xytext=(2.5, 300),
            arrowprops=dict(arrowstyle='->', color='#ED1C24', lw=1.5),
            fontsize=8, ha='center')
ax4.annotate('Vera Rubin', xy=(6, 450), xytext=(6.5, 490),
            arrowprops=dict(arrowstyle='->', color='#76B900', lw=1.5),
            fontsize=8, ha='center')
ax4.annotate('MI400', xy=(7, 500), xytext=(7.5, 540),
            arrowprops=dict(arrowstyle='->', color='#ED1C24', lw=1.5),
            fontsize=8, ha='center')

plt.tight_layout()
plt.savefig('/Users/steven/projects/layout_automation/gpu_performance_comparison.png',
            dpi=300, bbox_inches='tight')
print("GPU performance comparison chart saved as 'gpu_performance_comparison.png'")

# Create a second chart focusing on emerging players
fig2, (ax5, ax6) = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Emerging AI Accelerator Companies Performance', fontsize=16, fontweight='bold')

# 5. Specialized Performance Metrics
companies_emerging = ['NVIDIA\nH200\n(baseline)', 'AMD\nMI325X', 'Groq\nLPU', 'Cerebras\nWSE-3', 'Graphcore\nIPU', 'SambaNova\nSN40L']
# Different metrics: tokens/sec for inference
tokens_per_sec = [10000, 9500, 15000, 12000, 8000, 9000]  # Estimated relative values
colors_emerging = ['#76B900', '#ED1C24', '#FF6B35', '#4ECDC4', '#95E1D3', '#F38181']

bars3 = ax5.bar(range(len(companies_emerging)), tokens_per_sec, color=colors_emerging, alpha=0.8)
ax5.set_xticks(range(len(companies_emerging)))
ax5.set_xticklabels(companies_emerging, rotation=0, ha='center', fontsize=9)
ax5.set_ylabel('Inference Speed (Tokens/Second)', fontsize=10)
ax5.set_title('LLM Inference Performance Comparison', fontsize=12, fontweight='bold')
ax5.grid(axis='y', alpha=0.3)

for bar, val in zip(bars3, tokens_per_sec):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
             f'{val:,}', ha='center', va='bottom', fontsize=9)

# 6. Cost-Performance Ratio (lower is better)
companies_cost = ['NVIDIA\nH200', 'AMD\nMI325X', 'AMD\nMI350', 'Intel\nGaudi 3', 'Groq\nLPU', 'Cerebras\nWSE-3']
cost_performance = [100, 70, 65, 60, 85, 90]  # Relative cost per performance unit (lower = better value)
colors_cost = ['#76B900', '#ED1C24', '#ED1C24', '#0071C5', '#FF6B35', '#4ECDC4']

bars4 = ax6.barh(range(len(companies_cost)), cost_performance, color=colors_cost, alpha=0.8)
ax6.set_yticks(range(len(companies_cost)))
ax6.set_yticklabels(companies_cost, fontsize=9)
ax6.set_xlabel('Relative Cost per Performance (Lower = Better Value)', fontsize=10)
ax6.set_title('Cost-Performance Efficiency', fontsize=12, fontweight='bold')
ax6.grid(axis='x', alpha=0.3)
ax6.invert_xaxis()  # Invert so better (lower) values are on right

for bar, val in zip(bars4, cost_performance):
    ax6.text(bar.get_width() - 3, bar.get_y() + bar.get_height()/2,
             f'{val}', ha='right', va='center', fontsize=9, color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/steven/projects/layout_automation/emerging_gpu_performance.png',
            dpi=300, bbox_inches='tight')
print("Emerging GPU performance chart saved as 'emerging_gpu_performance.png'")

plt.show()
