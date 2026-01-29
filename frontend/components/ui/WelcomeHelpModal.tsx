/**
 * Welcome / Help Modal
 * Shown on first visit after signup and when user clicks Help in the nav.
 */

'use client';

import { useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';

const WELCOME_STORAGE_KEY = 'boosterboxpro_welcome_seen';

export function getWelcomeSeen(): boolean {
  if (typeof window === 'undefined') return true;
  return !!localStorage.getItem(WELCOME_STORAGE_KEY);
}

export function setWelcomeSeen(): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(WELCOME_STORAGE_KEY, '1');
}

interface WelcomeHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function WelcomeHelpModal({ isOpen, onClose }: WelcomeHelpModalProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  const handleClose = useCallback(() => onClose(), [onClose]);

  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = 'unset';
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, handleClose]);

  useEffect(() => {
    if (!isOpen || !panelRef.current) return;
    const focusables = panelRef.current.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    first?.focus();
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    panelRef.current.addEventListener('keydown', onKeyDown);
    return () => panelRef.current?.removeEventListener('keydown', onKeyDown);
  }, [isOpen]);

  if (!isOpen) return null;

  const content = (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="welcome-title"
    >
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={handleClose}
        aria-hidden="true"
      />
      <div
        ref={panelRef}
        className="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl border border-white/15 shadow-2xl"
        style={{ background: 'linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%)' }}
        onClick={(e) => e.stopPropagation()}
        role="document"
      >
        <div className="p-6 sm:p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 id="welcome-title" className="text-xl font-bold text-white">
              How to use BoosterBoxPro
            </h2>
            <button
              type="button"
              onClick={handleClose}
              className="p-2 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-4 text-white/85 text-sm">
            <p>
              <strong className="text-white">Dashboard</strong> — The leaderboard shows all tracked booster boxes ranked by volume. Use the <strong>time range</strong> (24h / 7d / 30d) to switch between daily, weekly, or monthly metrics.
            </p>
            <p>
              <strong className="text-white">Sorting</strong> — Click any column header (Floor, Volume, Sales, Days to 20%, etc.) to sort the table. Click again to toggle ascending/descending.
            </p>
            <p>
              <strong className="text-white">Box details</strong> — Click any row to open that box’s detail page for floor price, sales per day, days to +20%, and more.
            </p>
            <p>
              <strong className="text-white">Account</strong> — Use the Account link in the nav to manage your subscription and profile.
            </p>
            <p className="text-white/60 text-xs pt-2">
              You can reopen this guide anytime from the Help button in the top navigation.
            </p>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 rounded-full bg-white/15 hover:bg-white/25 text-white font-medium transition-colors"
            >
              Got it
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
}
