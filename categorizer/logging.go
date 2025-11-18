package main

import (
	"encoding/json"
	"log"
	"os"
	"time"
)

// LogLevel represents different log levels
type LogLevel string

const (
	INFO  LogLevel = "INFO"
	WARN  LogLevel = "WARN"
	ERROR LogLevel = "ERROR"
)

// LogEntry represents a structured log entry
type LogEntry struct {
	Timestamp   string      `json:"timestamp"`
	Level       LogLevel    `json:"level"`
	Service     string      `json:"service"`
	Version     string      `json:"version"`
	Message     string      `json:"message"`
	Merchant    string      `json:"merchant,omitempty"`
	Category    string      `json:"category,omitempty"`
	Amount      float64     `json:"amount,omitempty"`
	Duration    string      `json:"duration_ms,omitempty"`
	StatusCode  string      `json:"status_code,omitempty"`
	Method      string      `json:"method,omitempty"`
	Endpoint    string      `json:"endpoint,omitempty"`
	EventType   string      `json:"event_type,omitempty"`
	ErrorType   string      `json:"error_type,omitempty"`
	RequestID   string      `json:"request_id,omitempty"`
}

// StructuredLogger provides structured JSON logging
type StructuredLogger struct {
	logger *log.Logger
}

// NewStructuredLogger creates a new structured logger
func NewStructuredLogger() *StructuredLogger {
	return &StructuredLogger{
		logger: log.New(os.Stdout, "", 0),
	}
}

// logEntry logs a structured entry
func (sl *StructuredLogger) logEntry(level LogLevel, message string, fields map[string]interface{}) {
	entry := LogEntry{
		Timestamp: time.Now().UTC().Format(time.RFC3339Nano),
		Level:     level,
		Service:   "categorizer",
		Version:   "1.0.0",
		Message:   message,
	}

	// Populate fields from map
	if merchant, ok := fields["merchant"].(string); ok {
		entry.Merchant = merchant
	}
	if category, ok := fields["category"].(string); ok {
		entry.Category = category
	}
	if amount, ok := fields["amount"].(float64); ok {
		entry.Amount = amount
	}
	if duration, ok := fields["duration"].(time.Duration); ok {
		entry.Duration = duration.String()
	}
	if statusCode, ok := fields["status_code"].(string); ok {
		entry.StatusCode = statusCode
	}
	if method, ok := fields["method"].(string); ok {
		entry.Method = method
	}
	if endpoint, ok := fields["endpoint"].(string); ok {
		entry.Endpoint = endpoint
	}
	if eventType, ok := fields["event_type"].(string); ok {
		entry.EventType = eventType
	}
	if errorType, ok := fields["error_type"].(string); ok {
		entry.ErrorType = errorType
	}
	if requestID, ok := fields["request_id"].(string); ok {
		entry.RequestID = requestID
	}

	jsonData, err := json.Marshal(entry)
	if err != nil {
		sl.logger.Printf("Failed to marshal log entry: %v", err)
		return
	}

	sl.logger.Println(string(jsonData))
}

// Info logs an info level message
func (sl *StructuredLogger) Info(message string, fields map[string]interface{}) {
	sl.logEntry(INFO, message, fields)
}

// Warn logs a warning level message
func (sl *StructuredLogger) Warn(message string, fields map[string]interface{}) {
	sl.logEntry(WARN, message, fields)
}

// Error logs an error level message
func (sl *StructuredLogger) Error(message string, fields map[string]interface{}) {
	sl.logEntry(ERROR, message, fields)
}

// Global structured logger instance
var structuredLogger = NewStructuredLogger()

// Helper functions for common log patterns
func logCategorizationRequest(merchant, category string, amount float64, duration time.Duration, success bool) {
	level := INFO
	message := "Categorization request completed"
	
	if !success {
		level = WARN
		message = "Categorization request failed"
	}

	fields := map[string]interface{}{
		"merchant":    merchant,
		"category":    category,
		"amount":      amount,
		"duration":    duration,
		"event_type":  "categorization_request",
		"success":     success,
	}

	if level == INFO {
		structuredLogger.Info(message, fields)
	} else {
		structuredLogger.Warn(message, fields)
	}
}

func logHTTPRequest(method, endpoint, statusCode string, duration time.Duration) {
	level := INFO
	if statusCode[0] >= '4' {
		level = WARN
	}

	message := "HTTP request processed"
	fields := map[string]interface{}{
		"method":      method,
		"endpoint":    endpoint,
		"status_code": statusCode,
		"duration":    duration,
		"event_type":  "http_request",
	}

	if level == INFO {
		structuredLogger.Info(message, fields)
	} else {
		structuredLogger.Warn(message, fields)
	}
}

func logServiceStartup(port string) {
	structuredLogger.Info("Service started", map[string]interface{}{
		"port":       port,
		"event_type": "service_startup",
	})
}

func logCategorizationError(errorType, errorMessage string) {
	structuredLogger.Error("Categorization error occurred", map[string]interface{}{
		"error_type":    errorType,
		"error_message": errorMessage,
		"event_type":    "categorization_error",
	})
}