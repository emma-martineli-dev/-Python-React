"use client";

import { FormEvent, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";

const MAX_TITLE_LEN = 255;
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const ALLOWED_EXTENSIONS = new Set([
  ".jpg", ".jpeg", ".png", ".gif", ".webp",
  ".pdf", ".txt", ".csv", ".json", ".xml",
  ".zip", ".tar", ".gz",
  ".exe", ".bat", ".cmd", ".sh", ".js",
]);

type Props = {
  show: boolean;
  onHide: () => void;
  onUpload: (title: string, file: File) => Promise<void>;
};

function getExtension(filename: string): string {
  const idx = filename.lastIndexOf(".");
  return idx >= 0 ? filename.slice(idx).toLowerCase() : "";
}

export function UploadModal({ show, onHide, onUpload }: Props) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function validate(): string | null {
    if (!title.trim()) return "Укажите название файла";
    if (title.trim().length > MAX_TITLE_LEN) return `Название не должно превышать ${MAX_TITLE_LEN} символов`;
    if (!selectedFile) return "Выберите файл";
    if (selectedFile.size === 0) return "Файл пустой";
    if (selectedFile.size > MAX_FILE_SIZE) return "Файл превышает максимальный размер 100 МБ";
    const ext = getExtension(selectedFile.name);
    if (!ext) return "Файл должен иметь расширение";
    if (!ALLOWED_EXTENSIONS.has(ext)) return `Расширение «${ext}» не поддерживается`;
    return null;
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await onUpload(title.trim(), selectedFile!);
      handleHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleHide() {
    setTitle("");
    setSelectedFile(null);
    setError(null);
    setIsSubmitting(false);
    onHide();
  }

  return (
    <Modal show={show} onHide={handleHide} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && <div className="alert alert-danger py-2">{error}</div>}
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Например, Договор с подрядчиком"
              maxLength={MAX_TITLE_LEN}
            />
            <Form.Text className="text-muted">{title.length} / {MAX_TITLE_LEN}</Form.Text>
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              accept={[...ALLOWED_EXTENSIONS].join(",")}
              onChange={(e) => setSelectedFile((e.target as HTMLInputElement).files?.[0] ?? null)}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={handleHide}>Отмена</Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
