/**
 * Advanced Analytics for Smart Digital Twin
 * Comprehensive data visualization and insights
 */

class AnalyticsEngine {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        this.loadAnalyticsData();
    }

    async loadAnalyticsData() {
        try {
            const response = await fetch('/statistics');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.data = await response.json();
            this.renderAnalytics();
            this.createCharts();
        } catch (error) {
            console.error('Analytics loading failed:', error);
            this.renderErrorState();
        }
    }

    renderAnalytics() {
        this.renderMetricCards();
        this.renderDetailedAnalytics();
        this.renderProductivityInsights();
    }

    renderMetricCards() {
        const overview = this.data.overview || {};
        
        // Update metric cards
        document.getElementById('totalMemories').textContent = overview.total_memories || 0;
        document.getElementById('successRate').textContent = `${Math.round(overview.success_rate || 0)}%`;
        document.getElementById('totalInsights').textContent = overview.total_insights || 0;
        document.getElementById('avgInsights').textContent = overview.avg_insights_per_task || 0;

        // Update change indicators (placeholder for now)
        this.updateChangeIndicator('memoriesChange', '+12%', 'positive');
        this.updateChangeIndicator('successChange', '+5%', 'positive');
        this.updateChangeIndicator('insightsChange', '+23%', 'positive');
        this.updateChangeIndicator('avgChange', '+8%', 'positive');
    }

    updateChangeIndicator(elementId, value, trend) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            element.className = `metric-change ${trend}`;
        }
    }

    renderDetailedAnalytics() {
        const container = document.getElementById('detailedAnalytics');
        if (!container) return;

        const byAction = this.data.by_action || { counts: {}, details: {} };
        const timeAnalytics = this.data.time_analytics || {};

        let html = `
            <div class="analytics-section">
                <h6 class="section-title">Performance by Action Type</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Action Type</th>
                                <th>Total</th>
                                <th>Completed</th>
                                <th>Success Rate</th>
                                <th>Avg Time</th>
                                <th>Total Insights</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        for (const [action, counts] of Object.entries(byAction.counts)) {
            const details = byAction.details[action] || {};
            const successRate = details.success_rate || 0;
            const avgTime = details.avg_processing_time || 0;
            const totalInsights = details.total_insights || 0;

            html += `
                <tr>
                    <td>
                        <span class="action-badge action-${action}">
                            <i class="${this.getActionIcon(action)}"></i>
                            ${this.getActionLabel(action)}
                        </span>
                    </td>
                    <td>${counts.total}</td>
                    <td>${counts.completed}</td>
                    <td>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: ${successRate}%"></div>
                            <span class="progress-text">${Math.round(successRate)}%</span>
                        </div>
                    </td>
                    <td>${this.formatTime(avgTime)}</td>
                    <td>
                        <span class="insight-count">${totalInsights}</span>
                    </td>
                </tr>
            `;
        }

        html += `
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="analytics-section">
                <h6 class="section-title">Time-based Analytics</h6>
                <div class="time-metrics">
                    <div class="time-metric">
                        <div class="time-value">${timeAnalytics.today || 0}</div>
                        <div class="time-label">Today</div>
                    </div>
                    <div class="time-metric">
                        <div class="time-value">${timeAnalytics.this_week || 0}</div>
                        <div class="time-label">This Week</div>
                    </div>
                    <div class="time-metric">
                        <div class="time-value">${timeAnalytics.this_month || 0}</div>
                        <div class="time-label">This Month</div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    renderProductivityInsights() {
        const container = document.getElementById('productivityInsights');
        if (!container) return;

        const metrics = this.data.productivity_metrics || {};
        const overview = this.data.overview || {};

        const insights = [
            {
                icon: 'fas fa-file-alt',
                label: 'Documents',
                value: metrics.documents_processed || 0,
                trend: '+15%',
                color: 'primary'
            },
            {
                icon: 'fas fa-users',
                label: 'Meetings',
                value: metrics.meetings_processed || 0,
                trend: '+8%',
                color: 'success'
            },
            {
                icon: 'fas fa-envelope',
                label: 'Emails',
                value: metrics.emails_drafted || 0,
                trend: '+22%',
                color: 'warning'
            },
            {
                icon: 'fas fa-question-circle',
                label: 'Questions',
                value: metrics.questions_generated || 0,
                trend: '+18%',
                color: 'info'
            }
        ];

        let html = `
            <div class="insights-grid">
                ${insights.map(insight => `
                    <div class="insight-item">
                        <div class="insight-icon text-${insight.color}">
                            <i class="${insight.icon}"></i>
                        </div>
                        <div class="insight-content">
                            <div class="insight-value">${insight.value}</div>
                            <div class="insight-label">${insight.label}</div>
                            <div class="insight-trend positive">${insight.trend}</div>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="productivity-summary">
                <h6>Quick Stats</h6>
                <ul class="stats-list">
                    <li>
                        <span class="stat-label">Total Processing Time:</span>
                        <span class="stat-value">${this.calculateTotalTime()}</span>
                    </li>
                    <li>
                        <span class="stat-label">Average per Day:</span>
                        <span class="stat-value">${this.calculateDailyAverage()}</span>
                    </li>
                    <li>
                        <span class="stat-label">Most Productive Action:</span>
                        <span class="stat-value">${this.getMostProductiveAction()}</span>
                    </li>
                    <li>
                        <span class="stat-label">Efficiency Score:</span>
                        <span class="stat-value">${Math.round(overview.success_rate || 0)}%</span>
                    </li>
                </ul>
            </div>
        `;

        container.innerHTML = html;
    }

    createCharts() {
        this.createMemoryGrowthChart();
        this.createActivityDistributionChart();
    }

    createMemoryGrowthChart() {
        const ctx = document.getElementById('memoryGrowthChart');
        if (!ctx) return;

        const memoryGrowth = this.data.memory_growth || { dates: [], counts: [] };
        
        if (this.charts.memoryGrowth) {
            this.charts.memoryGrowth.destroy();
        }

        this.charts.memoryGrowth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: memoryGrowth.dates,
                datasets: [{
                    label: 'Memories Created',
                    data: memoryGrowth.counts,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createActivityDistributionChart() {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        const distribution = this.data.action_distribution || { labels: [], data: [] };
        
        if (this.charts.activity) {
            this.charts.activity.destroy();
        }

        const colors = [
            '#2563eb', // blue
            '#10b981', // green
            '#f59e0b', // yellow
            '#06b6d4', // cyan
            '#8b5cf6'  // purple
        ];

        this.charts.activity = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: distribution.labels.map(label => this.getActionLabel(label)),
                datasets: [{
                    data: distribution.data,
                    backgroundColor: colors.slice(0, distribution.labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    // Utility functions
    getActionIcon(action) {
        const icons = {
            'document_analysis': 'fas fa-file-alt',
            'meeting_processing': 'fas fa-users',
            'email_drafting': 'fas fa-envelope',
            'smart_questions': 'fas fa-question-circle',
            'custom': 'fas fa-cog'
        };
        return icons[action] || 'fas fa-circle';
    }

    getActionLabel(action) {
        const labels = {
            'document_analysis': 'Documents',
            'meeting_processing': 'Meetings',
            'email_drafting': 'Emails',
            'smart_questions': 'Questions',
            'custom': 'Custom'
        };
        return labels[action] || action;
    }

    formatTime(seconds) {
        if (seconds < 60) return `${Math.round(seconds)}s`;
        if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
        return `${Math.round(seconds / 3600)}h`;
    }

    calculateTotalTime() {
        // Placeholder calculation
        const overview = this.data.overview || {};
        return `${Math.round((overview.total_memories || 0) * 2.5)}m`;
    }

    calculateDailyAverage() {
        const timeAnalytics = this.data.time_analytics || {};
        const weeklyAvg = (timeAnalytics.this_week || 0) / 7;
        return `${Math.round(weeklyAvg * 10) / 10}/day`;
    }

    getMostProductiveAction() {
        const byAction = this.data.by_action || { counts: {} };
        let maxAction = '';
        let maxCount = 0;

        for (const [action, counts] of Object.entries(byAction.counts)) {
            if (counts.completed > maxCount) {
                maxCount = counts.completed;
                maxAction = action;
            }
        }

        return this.getActionLabel(maxAction) || 'None';
    }

    renderErrorState() {
        const containers = ['detailedAnalytics', 'productivityInsights'];
        containers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-exclamation-triangle mb-2 d-block"></i>
                        <p class="mb-0">Analytics temporarily unavailable</p>
                    </div>
                `;
            }
        });
    }

    refresh() {
        this.loadAnalyticsData();
    }
}

// Global functions
function refreshChart(type) {
    if (window.analyticsEngine) {
        window.analyticsEngine.refresh();
    }
}

// Initialize analytics when tab is activated
document.addEventListener('DOMContentLoaded', () => {
    const analyticsTab = document.getElementById('analytics-tab');
    if (analyticsTab) {
        analyticsTab.addEventListener('shown.bs.tab', () => {
            if (!window.analyticsEngine) {
                window.analyticsEngine = new AnalyticsEngine();
            } else {
                window.analyticsEngine.refresh();
            }
        });
    }
});