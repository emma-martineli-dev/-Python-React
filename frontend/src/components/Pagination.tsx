"use client";

import { Button } from "react-bootstrap";

type Props = {
  offset: number;
  total: number;
  pageSize: number;
  onPage: (offset: number) => void;
};

export function Pagination({ offset, total, pageSize, onPage }: Props) {
  const page = Math.floor(offset / pageSize);
  const totalPages = Math.ceil(total / pageSize);

  if (totalPages <= 1) return null;

  return (
    <div className="d-flex justify-content-center align-items-center gap-2 mt-3">
      <Button
        variant="outline-secondary"
        size="sm"
        disabled={page === 0}
        onClick={() => onPage((page - 1) * pageSize)}
      >
        ←
      </Button>
      <span className="small text-secondary">
        {page + 1} / {totalPages}
      </span>
      <Button
        variant="outline-secondary"
        size="sm"
        disabled={page >= totalPages - 1}
        onClick={() => onPage((page + 1) * pageSize)}
      >
        →
      </Button>
    </div>
  );
}
