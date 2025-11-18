import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Account } from "@/types";
import { formatCurrency } from "@/utils/currency";
import { Wallet, TrendingUp, DollarSign, CreditCard } from "lucide-react";

interface AccountOverviewCardsProps {
  accounts: Account[];
  totalBalance: number;
  recentTransactionsCount: number;
}

export function AccountOverviewCards({
  accounts,
  totalBalance,
  recentTransactionsCount,
}: AccountOverviewCardsProps) {
  const currentAccount = accounts.find((acc) => acc.name.includes("Current"));
  const savingsAccount = accounts.find((acc) => acc.name.includes("Savings"));

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Balance */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatCurrency(totalBalance)}
          </div>
          <p className="text-xs text-muted-foreground">
            Across {accounts.length} accounts
          </p>
        </CardContent>
      </Card>

      {/* Current Account */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Current Account</CardTitle>
          <CreditCard className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {currentAccount ? formatCurrency(currentAccount.balance) : "$0.00"}
          </div>
          <p className="text-xs text-muted-foreground">
            Daily spending account
          </p>
        </CardContent>
      </Card>

      {/* Savings Account */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Savings Account</CardTitle>
          <Wallet className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {savingsAccount ? formatCurrency(savingsAccount.balance) : "$0.00"}
          </div>
          <p className="text-xs text-muted-foreground">Long-term savings</p>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{recentTransactionsCount}</div>
          <p className="text-xs text-muted-foreground">
            Transactions this week
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

interface AccountCardsGridProps {
  accounts: Account[];
  selectedAccount: Account | null;
  onAccountSelect: (account: Account) => void;
  onTriggerTopUp: (accountId: number) => void;
  triggeringTopUp: number | null;
}

export function AccountCardsGrid({
  accounts,
  selectedAccount,
  onAccountSelect,
  onTriggerTopUp,
  triggeringTopUp,
}: AccountCardsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {accounts.map((account) => (
        <Card
          key={account.id}
          className={`cursor-pointer transition-all hover:shadow-md ${
            selectedAccount?.id === account.id
              ? "ring-2 ring-blue-500 shadow-md"
              : ""
          }`}
          onClick={() => onAccountSelect(account)}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="flex items-center space-x-2">
              <Wallet className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-base font-medium">
                {account.name}
              </CardTitle>
            </div>
            {selectedAccount?.id === account.id && (
              <Badge variant="default" className="text-xs">
                Active
              </Badge>
            )}
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {formatCurrency(account.balance)}
            </div>
            <div className="flex items-center justify-between">
              <CardDescription>
                Account ID: {account.uuid.slice(-8)}
              </CardDescription>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onTriggerTopUp(account.id);
                }}
                disabled={triggeringTopUp === account.id}
                className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition-colors disabled:opacity-50"
              >
                {triggeringTopUp === account.id ? "TopUp..." : "TopUp"}
              </button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

interface AccountCardsDisplayProps {
  accounts: Account[];
}

export function AccountCardsDisplay({ accounts }: AccountCardsDisplayProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {accounts.map((account) => (
        <Card key={account.id} className="transition-all hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="flex items-center space-x-2">
              <Wallet className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-base font-medium">
                {account.name}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {formatCurrency(account.balance)}
            </div>
            <CardDescription>
              Account ID: {account.uuid.slice(-8)}
            </CardDescription>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
