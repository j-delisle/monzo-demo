import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Transaction, Account } from "@/types";
import { formatCurrency } from "@/utils/currency";
import {
  ArrowUpDown,
  TrendingUp,
  TrendingDown,
  Calendar,
  Download,
  Plus,
} from "lucide-react";
import { NewTransactionModal } from "@/components/NewTransactionModal";

interface TransactionsTableProps {
  transactions: Transaction[];
  loading?: boolean;
  accounts?: Account[];
  onTransactionCreated?: () => void;
}

export function TransactionsTable({
  transactions,
  loading = false,
  accounts = [],
  onTransactionCreated,
}: TransactionsTableProps) {
  const [sortBy, setSortBy] = useState<"date" | "amount" | "merchant">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Get unique categories for filter
  const categories = [
    "all",
    ...new Set(
      transactions
        .map((t) => t.category)
        .filter((cat): cat is string => Boolean(cat)),
    ),
  ];

  // Sort and filter transactions
  const filteredTransactions = transactions
    .filter(
      (transaction) =>
        filterCategory === "all" || transaction.category === filterCategory,
    )
    .sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "date":
          comparison =
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case "amount":
          comparison = a.amount - b.amount;
          break;
        case "merchant":
          comparison = a.merchant.localeCompare(b.merchant);
          break;
      }

      return sortOrder === "desc" ? -comparison : comparison;
    });

  const handleSort = (column: "date" | "amount" | "merchant") => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("desc");
    }
  };

  const formatDate = (date: string | Date) => {
    return new Date(date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      "Food & Drink": "bg-orange-100 text-orange-800",
      Transport: "bg-blue-100 text-blue-800",
      Shopping: "bg-purple-100 text-purple-800",
      Groceries: "bg-green-100 text-green-800",
      Entertainment: "bg-pink-100 text-pink-800",
      "Bills & Utilities": "bg-red-100 text-red-800",
      Income: "bg-emerald-100 text-emerald-800",
      Other: "bg-gray-100 text-gray-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ArrowUpDown className="h-5 w-5" />
            Transactions
          </CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filterCategory || "all"}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category === "all" ? "All Categories" : category}
                </option>
              ))}
            </select>
            {accounts.length > 0 && (
              <Button onClick={() => setIsModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Transaction
              </Button>
            )}
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => handleSort("date")}
                >
                  <div className="flex items-center gap-2">
                    Date
                    <Calendar className="h-4 w-4" />
                    {sortBy === "date" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </div>
                </TableHead>
                <TableHead
                  className="cursor-pointer select-none"
                  onClick={() => handleSort("merchant")}
                >
                  <div className="flex items-center gap-2">
                    Merchant
                    {sortBy === "merchant" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </div>
                </TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Category</TableHead>
                <TableHead
                  className="text-right cursor-pointer select-none"
                  onClick={() => handleSort("amount")}
                >
                  <div className="flex items-center justify-end gap-2">
                    Amount
                    {sortBy === "amount" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </div>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTransactions.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="text-center py-8 text-muted-foreground"
                  >
                    No transactions found
                  </TableCell>
                </TableRow>
              ) : (
                filteredTransactions.map((transaction) => (
                  <TableRow key={transaction.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="font-medium">
                        {formatDate(transaction.timestamp)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{transaction.merchant}</div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-muted-foreground max-w-[200px] truncate">
                        {transaction.description}
                      </div>
                    </TableCell>
                    <TableCell>
                      {transaction.category && (
                        <Badge
                          variant="secondary"
                          className={`${getCategoryColor(transaction.category)} text-xs`}
                        >
                          {transaction.category}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div
                        className={`font-medium flex items-center justify-end gap-1 ${
                          transaction.transaction_type === "credit"
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {transaction.transaction_type === "credit" ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        {transaction.transaction_type === "credit" ? "+" : "-"}
                        {formatCurrency(transaction.amount)}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {filteredTransactions.length > 0 && (
          <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
            <div>
              Showing {filteredTransactions.length} of {transactions.length}{" "}
              transactions
            </div>
            <div>
              Total:{" "}
              {formatCurrency(
                filteredTransactions.reduce(
                  (sum, t) =>
                    sum +
                    (t.transaction_type === "credit" ? t.amount : -t.amount),
                  0,
                ),
              )}
            </div>
          </div>
        )}
      </CardContent>

      <NewTransactionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        accounts={accounts}
        onTransactionCreated={() => {
          onTransactionCreated?.();
          setIsModalOpen(false);
        }}
      />
    </Card>
  );
}
