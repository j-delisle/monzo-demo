package main

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

type TransactionRequest struct {
	Merchant    string  `json:"merchant" binding:"required"`
	Amount      float64 `json:"amount" binding:"required"`
	Description string  `json:"description"`
}

type CategoryResponse struct {
	Category string `json:"category"`
}

func categorizeTransaction(merchant, description string, amount float64) string {
	merchantLower := strings.ToLower(merchant)
	descriptionLower := strings.ToLower(description)

	// Transport
	transportKeywords := []string{"uber", "lyft", "taxi", "transport", "tfl", "bus", "train", "metro", "subway"}
	for _, keyword := range transportKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Transport"
		}
	}

	// Food & Drink
	foodKeywords := []string{"starbucks", "costa", "cafe", "restaurant", "mcdonalds", "kfc", "pizza", "food", "coffee", "tea"}
	for _, keyword := range foodKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Food & Drink"
		}
	}

	// Shopping
	shoppingKeywords := []string{"amazon", "ebay", "shop", "store", "retail", "market", "mall", "clothing", "fashion"}
	for _, keyword := range shoppingKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Shopping"
		}
	}

	// Groceries
	groceryKeywords := []string{"tesco", "sainsbury", "asda", "morrisons", "waitrose", "aldi", "lidl", "grocery", "supermarket"}
	for _, keyword := range groceryKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Groceries"
		}
	}

	// Entertainment
	entertainmentKeywords := []string{"cinema", "movie", "netflix", "spotify", "apple music", "game", "entertainment", "theatre"}
	for _, keyword := range entertainmentKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Entertainment"
		}
	}

	// Bills & Utilities
	billsKeywords := []string{"electric", "gas", "water", "internet", "phone", "insurance", "council tax", "utility", "energy"}
	for _, keyword := range billsKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Bills & Utilities"
		}
	}

	// ATM/Cash
	if strings.Contains(merchantLower, "atm") || strings.Contains(merchantLower, "cash") {
		return "ATM"
	}

	// Large amounts might be rent/salary
	if amount > 500 {
		if strings.Contains(descriptionLower, "salary") || strings.Contains(descriptionLower, "wages") {
			return "Income"
		}
		if strings.Contains(descriptionLower, "rent") || strings.Contains(descriptionLower, "mortgage") {
			return "Housing"
		}
	}

	return "Other"
}

func handleCategorize(c *gin.Context) {
	var req TransactionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	category := categorizeTransaction(req.Merchant, req.Description, req.Amount)

	response := CategoryResponse{
		Category: category,
	}

	c.JSON(http.StatusOK, response)
}

func main() {
	r := gin.Default()

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "categorizer",
		})
	})

	// Categorization endpoint
	r.POST("/categorize", handleCategorize)

	// Start server
	r.Run(":9000")
}
