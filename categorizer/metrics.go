package main

import (
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// Prometheus metrics
var (
	categorizationRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "categorization_requests_total",
			Help: "Total number of categorization requests",
		},
		[]string{"category", "status"},
	)

	categorizationErrorsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "categorization_errors_total",
			Help: "Total number of categorization errors",
		},
		[]string{"error_type"},
	)

	categorizationDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "categorization_duration_seconds",
			Help:    "Categorization request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"category"},
	)

	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status_code"},
	)

	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)
)

// Helper functions for recording metrics
func recordCategorizationRequest(category, status string) {
	categorizationRequestsTotal.WithLabelValues(category, status).Inc()
}

func recordCategorizationError(errorType string) {
	categorizationErrorsTotal.WithLabelValues(errorType).Inc()
}

func recordCategorizationDuration(category string, duration time.Duration) {
	categorizationDuration.WithLabelValues(category).Observe(duration.Seconds())
}

func recordHTTPRequest(method, endpoint, statusCode string) {
	httpRequestsTotal.WithLabelValues(method, endpoint, statusCode).Inc()
}

func recordHTTPDuration(method, endpoint string, duration time.Duration) {
	httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration.Seconds())
}

// Middleware to track HTTP metrics
func MetricsMiddleware() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		duration := time.Since(start)
		statusCode := strconv.Itoa(c.Writer.Status())

		// Record metrics
		recordHTTPRequest(method, path, statusCode)
		recordHTTPDuration(method, path, duration)
		
		// Log HTTP request
		logHTTPRequest(method, path, statusCode, duration)
	})
}