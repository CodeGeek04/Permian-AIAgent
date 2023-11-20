import matplotlib.pyplot as plt

accuracy = [76, 100]
experiment_number = ['last week', 'this week']

fig, ax = plt.subplots(figsize=(6, 4))

ax.plot(experiment_number, accuracy, '-o', label='comprehensibility')
bar_width = 0.35
bar1 = ax.bar(experiment_number, accuracy, bar_width, alpha=0.5)
ax.set_xlabel('Prompt Redesign with KMeans + ICIL')
ax.set_ylabel('Comprehensibility %')

ax.set_title('Comprehensibility on fixed dataset')
ax.legend(loc='best')
fig.tight_layout()

plt.savefig('demo/comprehensibility_chart.png')
plt.show()
