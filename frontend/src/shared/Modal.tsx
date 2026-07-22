import { Check, X } from "lucide-react";
import { useEffect, type ReactNode, type MouseEvent } from "react";

export function Modal({
  onClose,
  children,
  className,
}: {
  onClose: () => void;
  children: ReactNode;
  className?: string;
}) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [onClose]);

  const stop = (e: MouseEvent) => e.stopPropagation();

  return (
    <div
      className={className ? `modal-backdrop ${className}` : "modal-backdrop"}
      onClick={onClose}
    >
      <div className="modal-box" onClick={stop}>
        <button
          className="modal-close"
          type="button"
          onClick={onClose}
          aria-label="Закрыть"
        >
          ×
        </button>
        {children}
      </div>
    </div>
  );
}

export function ConfirmDialog({
  message,
  confirmLabel,
  pendingLabel,
  pending,
  onConfirm,
  onCancel,
}: {
  message: string;
  confirmLabel: string;
  pendingLabel: string;
  pending: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", handleKey);

    return () => document.removeEventListener("keydown", handleKey);
  }, [onCancel]);

  const stop = (e: MouseEvent) => e.stopPropagation();

  return (
    <div className="confirm-backdrop" onClick={onCancel}>
      <div className="confirm-box" onClick={stop}>
        <p className="confirm-message">{message}</p>
        <div className="confirm-actions">
          <button
            className="button"
            type="button"
            disabled={pending}
            onClick={onConfirm}
          >
            <Check size={16} />
            {pending ? pendingLabel : confirmLabel}
          </button>
          <button
            className="button button-secondary"
            type="button"
            disabled={pending}
            onClick={onCancel}
          >
            <X size={16} />
            Отмена
          </button>
        </div>
      </div>
    </div>
  );
}
