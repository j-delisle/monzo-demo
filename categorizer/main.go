package main

import (
	"log"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
)

type TransactionRequest struct {
	Merchant        string  `json:"merchant" binding:"required"`
	Amount          float64 `json:"amount" binding:"required"`
	Description     string  `json:"description"`
	TransactionType string  `json:"transaction_type" binding:"required"`
}

type CategoryResponse struct {
	Category string `json:"category"`
}

func categorizeTransaction(merchant, description string, amount float64, transactionType string) string {
	merchantLower := strings.ToLower(merchant)
	descriptionLower := strings.ToLower(description)
	transactionTypeLower := strings.ToLower(transactionType)

	if transactionTypeLower == "credit" {
		return "Income"
	}

	incomeKeywords := []string{"salary", "deposit", "income", "gift"}
	for _, keyword := range incomeKeywords {
		if strings.Contains(merchantLower, keyword) || strings.Contains(descriptionLower, keyword) {
			return "Income"
		}
	}

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
	if amount > 700 {
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
		log.Printf("Bad request: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	log.Printf("Categorizing transaction - Merchant: %s, Amount: %.2f, Credit: %t", req.Merchant, req.Amount, req.TransactionType)

	category := categorizeTransaction(req.Merchant, req.Description, req.Amount, req.TransactionType)

	log.Printf("Categorized as: %s", category)

	response := CategoryResponse{
		Category: category,
	}

	c.JSON(http.StatusOK, response)
}

func main() {
	log.Println("Starting categorizer service...")

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
	log.Println("Server listening on port 9000")
	r.Run(":9000")
}
