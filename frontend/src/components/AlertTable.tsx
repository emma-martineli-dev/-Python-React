"use client";

import { Badge, Spinner, Table } from "react-bootstrap";
import type { AlertItem } from "@/types";
import { Pagination } from "./Pagination";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function getLevelVariant(level: string) {
  if (level === "critical") return "danger";
  if (level === "warning") return "warning";
  return "success";
}

type Props = {
  items: AlertItem[];
  total: number;
  offset: number;
  pageSize: number;
  isLoading: boolean;
  onPage: (offset: number) => void;
};

export function AlertTable({ items, total, offset, pageSize, isLoading, onPage }: Props) {
  return (
    <>
      {isLoading ? (
        <div className="d-flex justify-content-center py-5">
          <Spinner animation="border" />
        </div>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle mb-0">
            <thead className="table-light">
              <tr>
                <th>ID</th>
                <th>File ID</th>
                <th>Уровень</th>
                <th>Сообщение</th>
                <th>Создан</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-4 text-secondary">
                    Алертов пока нет
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td className="small">{item.file_id}</td>
                    <td>
                      <Badge bg={getLevelVariant(item.level)}>{item.level}</Badge>
                    </td>
                    <td>{item.message}</td>
                    <td>{formatDate(item.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </div>
      )}
      <Pagination offset={offset} total={total} pageSize={pageSize} onPage={onPage} />
    </>
  );
}
