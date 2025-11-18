import { useState, useEffect } from "react";
import type { Account, Transaction } from "@/types";
import { accountsApi, transactionsApi, topUpApi } from "@/services/api";
import { DashboardLayout } from "@/components/DashboardLayout";
import {
  AccountOverviewCards,
  AccountCardsGrid,
  AccountCardsDisplay,
} from "@/components/AccountOverviewCards";
import { TransactionsTable } from "@/components/TransactionsTable";
import { TopUpRulesManager } from "@/components/TopUpRulesManager";
import { ObservabilityPage } from "@/components/ObservabilityPage";

export function Dashboard() {
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [currentView, setCurrentView] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [triggeringTopUp, setTriggeringTopUp] = useState<number | null>(null);

  const fetchAccounts = async () => {
    try {
      const data = await accountsApi.getAccounts();
      setAccounts(data);
      if (selectedAccount) {
        const updated = data.find((acc) => acc.id === selectedAccount.id);
        if (updated) {
          setSelectedAccount(updated);
        }
      }
      if (!selectedAccount && data.length > 0) {
        setSelectedAccount(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
    }
  };

  const fetchTransactions = async () => {
    try {
      const data = await transactionsApi.getTransactions();
      setTransactions(data);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchAccounts(), fetchTransactions()]);
      setLoading(false);
    };
    fetchData();
  }, [refreshTrigger]);

  const handleTransactionCreated = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleAccountSelect = (account: Account) => {
    setSelectedAccount(account);
  };

  const handleTriggerTopUp = async (accountId: number) => {
    setTriggeringTopUp(accountId);
    try {
      await topUpApi.triggerTopUp(accountId);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Failed to trigger topup:", error);
    } finally {
      setTriggeringTopUp(null);
    }
  };

  const totalBalance = accounts.reduce(
    (sum, account) => sum + account.balance,
    0,
  );
  const recentTransactionsCount = transactions.filter(
    (t) =>
      new Date(t.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
  ).length;

  const renderContent = () => {
    switch (currentView) {
      case "overview":
        return (
          <div className="space-y-6">
            <AccountOverviewCards
              accounts={accounts}
              totalBalance={totalBalance}
              recentTransactionsCount={recentTransactionsCount}
            />
            <div className="space-y-4">
              <AccountCardsDisplay accounts={accounts} />
            </div>
            <TransactionsTable
              transactions={transactions.slice(0, 10)}
              loading={loading}
            />
          </div>
        );

      case "accounts":
        return (
          <div className="space-y-6">
            <AccountOverviewCards
              accounts={accounts}
              totalBalance={totalBalance}
              recentTransactionsCount={recentTransactionsCount}
            />
            <AccountCardsGrid
              accounts={accounts}
              selectedAccount={selectedAccount}
              onAccountSelect={handleAccountSelect}
              onTriggerTopUp={handleTriggerTopUp}
              triggeringTopUp={triggeringTopUp}
            />
          </div>
        );

      case "transactions":
        return (
          <div className="space-y-6">
            <TransactionsTable
              transactions={transactions}
              loading={loading}
              accounts={accounts}
              onTransactionCreated={handleTransactionCreated}
            />
          </div>
        );

      case "topup":
        return (
          <div className="max-w-4xl mx-auto">
            <TopUpRulesManager accounts={accounts} />
          </div>
        );

      case "observability":
        return <ObservabilityPage />;

      default:
        return null;
    }
  };

  return (
    <DashboardLayout currentView={currentView} onViewChange={setCurrentView}>
      {renderContent()}
    </DashboardLayout>
  );
}
