import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AlertItem } from "@/types";

const PAGE_SIZE = 20;

export function useAlerts() {
  const [items, setItems] = useState<AlertItem[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (newOffset: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const page = await api.alerts.list(newOffset, PAGE_SIZE);
      setItems(page.items);
      setTotal(page.total);
      setOffset(newOffset);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { void load(0); }, [load]);

  return { items, total, offset, isLoading, error, load, pageSize: PAGE_SIZE };
}
