<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="header-content">
        <h1>Real-Time Analytics Dashboard</h1>
        <p class="creator-name">Created by Ravindra Singh Nagarkoti</p>
      </div>
      <div class="connection-status" :class="{ connected: isConnected }">
        {{ isConnected ? 'Connected' : 'Disconnected' }}
      </div>
    </header>

    <!-- Real-time Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>Active Users</h3>
          <div class="metric-value">{{ realTimeData.active_users || 0 }}</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <h3>Sales Today</h3>
          <div class="metric-value">₹{{ realTimeData.current_sales || 0 }}</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>Page Views/min</h3>
          <div class="metric-value">{{ realTimeData.page_views_per_minute || 0 }}</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🎯</div>
        <div class="metric-content">
          <h3>Conversion Rate</h3>
          <div class="metric-value">{{ realTimeData.conversion_rate || 0 }}%</div>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <div class="chart-container">
        <h3>User Growth</h3>
        <div ref="userChart" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>Sales Performance (₹)</h3>
        <div ref="salesChart" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>Page Views</h3>
        <div ref="pageViewsChart" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>Revenue Trend (₹)</h3>
        <div ref="revenueChart" class="chart"></div>
      </div>
    </div>

    <!-- Additional Metrics -->
    <div class="additional-metrics">
      <div class="metric-card">
        <h3>Bounce Rate</h3>
        <div class="metric-value">{{ realTimeData.bounce_rate || 0 }}%</div>
      </div>
      
      <div class="metric-card">
        <h3>Avg Session Duration</h3>
        <div class="metric-value">{{ formatDuration(realTimeData.avg_session_duration || 0) }}</div>
      </div>
      
      <div class="metric-card">
        <h3>Revenue/Hour</h3>
        <div class="metric-value">₹{{ realTimeData.revenue_per_hour || 0 }}</div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="dashboard-footer">
      <p>&copy; 2025 Analytics Dashboard by <strong>Ravindra Singh Nagarkoti</strong></p>
      <p class="footer-subtitle">Real-time data visualization with Vue.js & D3.js</p>
    </footer>
  </div>
</template>

<script>
import * as d3 from 'd3'
import { io } from 'socket.io-client'

export default {
  name: 'Dashboard',
  data() {
    return {
      socket: null,
      isConnected: false,
      realTimeData: {},
      analyticsData: {
        users: [],
        sales: [],
        page_views: [],
        conversions: [],
        revenue: []
      },
      resizeTimeout: null
    }
  },
  mounted() {
    this.initializeSocket()
    this.fetchInitialData()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.disconnect()
    }
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    initializeSocket() {
      this.socket = io('http://localhost:5001')
      
      this.socket.on('connect', () => {
        this.isConnected = true
        console.log('Connected to server')
      })
      
      this.socket.on('disconnect', () => {
        this.isConnected = false
        console.log('Disconnected from server')
      })
      
      this.socket.on('analytics_data', (data) => {
        this.analyticsData = data
        this.$nextTick(() => {
          this.createCharts()
        })
      })
      
      this.socket.on('real_time_data', (data) => {
        this.realTimeData = data
      })
    },
    
    async fetchInitialData() {
      try {
        const response = await fetch('http://localhost:5001/api/analytics')
        const data = await response.json()
        this.analyticsData = data
        this.$nextTick(() => {
          this.createCharts()
        })
      } catch (error) {
        console.error('Error fetching initial data:', error)
      }
    },
    
    createCharts() {
      this.createLineChart('userChart', this.analyticsData.users, 'count', 'Users')
      this.createLineChart('salesChart', this.analyticsData.sales, 'amount', 'Sales')
      this.createBarChart('pageViewsChart', this.analyticsData.page_views, 'count', 'Page Views')
      this.createLineChart('revenueChart', this.analyticsData.revenue, 'amount', 'Revenue')
    },
    
    createLineChart(containerRef, data, valueKey, label) {
      const container = this.$refs[containerRef]
      if (!container || !data.length) return
      
      // Clear previous chart
      d3.select(container).selectAll('*').remove()
      
      // Show only last 20 days for better clarity
      const displayData = data.slice(-20)
      
      const margin = { top: 20, right: 30, bottom: 50, left: 50 }
      const containerWidth = Math.max(400, container.clientWidth || 500)
      const width = containerWidth - margin.left - margin.right
      const height = 300 - margin.top - margin.bottom
      
      const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // Parse dates
      const parseTime = d3.timeParse('%Y-%m-%d')
      displayData.forEach(d => {
        d.date = parseTime(d.date)
        d.value = +d[valueKey]
      })
      
      // Scales
      const x = d3.scaleTime()
        .domain(d3.extent(displayData, d => d.date))
        .range([0, width])
      
      const y = d3.scaleLinear()
        .domain(d3.extent(displayData, d => d.value))
        .range([height, 0])
      
      // Line generator
      const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.value))
        .curve(d3.curveMonotoneX)
      
      // Add area under the line
      const area = d3.area()
        .x(d => x(d.date))
        .y0(height)
        .y1(d => y(d.value))
        .curve(d3.curveMonotoneX)
      
      g.append('path')
        .datum(displayData)
        .attr('fill', 'rgba(79, 70, 229, 0.1)')
        .attr('d', area)
      
      // Add line
      g.append('path')
        .datum(displayData)
        .attr('fill', 'none')
        .attr('stroke', '#4f46e5')
        .attr('stroke-width', 3)
        .attr('d', line)
      
      // Add dots
      g.selectAll('.dot')
        .data(displayData)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.value))
        .attr('r', 5)
        .attr('fill', '#4f46e5')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)
        .on('mouseover', function(event, d) {
          d3.select(this).attr('r', 7)
          // Show tooltip
          const tooltip = d3.select('body').append('div')
            .attr('class', 'chart-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('padding', '8px 12px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('opacity', 0)
          
          tooltip.transition().duration(200).style('opacity', 1)
          const formattedValue = label === 'Revenue' || label === 'Sales' ? `₹${d.value.toLocaleString()}` : d.value.toLocaleString()
          tooltip.html(`${d3.timeFormat('%m/%d')(d.date)}<br/>${label}: ${formattedValue}`)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
        })
        .on('mouseout', function(event, d) {
          d3.select(this).attr('r', 5)
          d3.selectAll('.chart-tooltip').remove()
        })
      
      // Add grid lines
      g.append('g')
        .attr('class', 'grid')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
          .tickSize(-height)
          .tickFormat('')
          .tickSizeOuter(0))
        .style('stroke', 'rgba(255, 255, 255, 0.1)')
        .style('stroke-dasharray', '2,2')
      
      g.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y)
          .tickSize(-width)
          .tickFormat('')
          .tickSizeOuter(0))
        .style('stroke', 'rgba(255, 255, 255, 0.1)')
        .style('stroke-dasharray', '2,2')
      
      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
          .tickFormat(d3.timeFormat('%m/%d'))
          .ticks(Math.min(8, displayData.length))
          .tickSizeOuter(0))
        .style('font-size', '11px')
        .style('fill', 'rgba(255, 255, 255, 0.8)')
      
      g.append('g')
        .call(d3.axisLeft(y)
          .tickFormat(d => {
            if (label === 'Revenue' || label === 'Sales') {
              return '₹' + d3.format('.0s')(d)
            }
            return d3.format('.0s')(d)
          })
          .ticks(5)
          .tickSizeOuter(0))
        .style('font-size', '11px')
        .style('fill', 'rgba(255, 255, 255, 0.8)')
    },
    
    createBarChart(containerRef, data, valueKey, label) {
      const container = this.$refs[containerRef]
      if (!container || !data.length) return
      
      // Clear previous chart
      d3.select(container).selectAll('*').remove()
      
      // Show only last 15 days to prevent overcrowding
      const displayData = data.slice(-15)
      
      const margin = { top: 20, right: 30, bottom: 50, left: 40 }
      const containerWidth = Math.max(400, container.clientWidth || 500)
      const width = containerWidth - margin.left - margin.right
      const height = 300 - margin.top - margin.bottom
      
      const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // Parse dates
      const parseTime = d3.timeParse('%Y-%m-%d')
      displayData.forEach(d => {
        d.date = parseTime(d.date)
        d.value = +d[valueKey]
      })
      
      // Scales
      const x = d3.scaleBand()
        .domain(displayData.map(d => d.date))
        .range([0, width])
        .padding(0.15)
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(displayData, d => d.value)])
        .range([height, 0])
      
      // Add bars
      g.selectAll('.bar')
        .data(displayData)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.date))
        .attr('width', x.bandwidth())
        .attr('y', d => y(d.value))
        .attr('height', d => height - y(d.value))
        .attr('fill', '#10b981')
        .on('mouseover', function(event, d) {
          d3.select(this).attr('fill', '#059669')
        })
        .on('mouseout', function(event, d) {
          d3.select(this).attr('fill', '#10b981')
        })
      
      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
          .tickFormat(d3.timeFormat('%m/%d'))
          .ticks(Math.min(8, displayData.length))
          .tickSizeOuter(0))
      
      g.append('g')
        .call(d3.axisLeft(y)
          .tickFormat(d => {
            if (label === 'Revenue' || label === 'Sales') {
              return '₹' + d3.format('.0s')(d)
            }
            return d3.format('.0s')(d)
          }))
    },
    
    formatDuration(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },
    
    handleResize() {
      // Debounce resize events
      clearTimeout(this.resizeTimeout)
      this.resizeTimeout = setTimeout(() => {
        if (this.analyticsData.users.length > 0) {
          this.createCharts()
        }
      }, 250)
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.creator-name {
  font-size: 1rem;
  opacity: 0.8;
  font-style: italic;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
}

.connection-status {
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 0, 0, 0.2);
  color: #ff6b6b;
  font-weight: 600;
  transition: all 0.3s ease;
}

.connection-status.connected {
  background: rgba(0, 255, 0, 0.2);
  color: #51cf66;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.metric-content h3 {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-container h3 {
  color: white;
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.chart {
  width: 100%;
  height: 350px;
  overflow: hidden;
  position: relative;
}

.chart svg {
  max-width: 100%;
  height: auto;
}

.chart .tick text {
  font-size: 11px;
  fill: rgba(255, 255, 255, 0.8);
}

.chart .tick line {
  stroke: rgba(255, 255, 255, 0.3);
}

.chart-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
}

.additional-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.additional-metrics .metric-card {
  flex-direction: column;
  text-align: center;
  padding: 15px;
}

.additional-metrics .metric-card h3 {
  font-size: 0.8rem;
  margin-bottom: 10px;
}

.additional-metrics .metric-value {
  font-size: 1.5rem;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  }
}

@media (max-width: 1000px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .dashboard-header h1 {
    font-size: 1.8rem;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .chart {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .charts-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .chart-container {
    padding: 15px;
  }
  
  .chart {
    height: 200px;
  }
  
  .metric-card {
    padding: 15px;
  }
}

.dashboard-footer {
  margin-top: 40px;
  padding: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.dashboard-footer p {
  margin: 5px 0;
  font-size: 0.9rem;
}

.footer-subtitle {
  font-size: 0.8rem !important;
  opacity: 0.6;
  font-style: italic;
}
</style>
