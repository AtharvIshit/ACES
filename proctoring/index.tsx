import React from 'react';
import { createRoot } from 'react-dom/client';
import { ProctoringManager } from './ProctoringManager';
import { BrutalistAdminQuery } from './BrutalistAdminQuery';

let isProctoringMounted = false;
// Expose rendering functions to the global window object
(window as any).mountProctoringManager = (elementId: string) => {
    if (isProctoringMounted) return; // Prevent double mounting

    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`Element heavily with ID ${elementId} not found`);
        return;
    }

    isProctoringMounted = true;
    const root = createRoot(el);
    root.render(<ProctoringManager onCriticalViolation={() => {
        window.alert('INTEGRITY COMPROMISED: Session terminated due to multiple violations.');

        // Extract attempt PK from current URL (e.g. /attempt/26/)
        const match = window.location.pathname.match(/\/attempt\/(\d+)\//);
        if (match) {
            const attemptPk = match[1];
            const csrfToken = (document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement)?.value || '';
            fetch(`/attempt/${attemptPk}/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: 'answers={}'
            }).then(res => res.json())
              .then(data => {
                  window.location.href = data.redirect || `/attempt/${attemptPk}/result/`;
              })
              .catch(() => {
                  window.location.href = `/attempt/${attemptPk}/result/`;
              });
        } else {
            window.location.href = '/dashboard/';
        }
    }} />);
};

let isAdminMounted = false;
(window as any).mountBrutalistAdminQuery = (elementId: string) => {
    if (isAdminMounted) return;
    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`Element heavily with ID ${elementId} not found`);
        return;
    }

    isAdminMounted = true;
    const root = createRoot(el);
    root.render(<BrutalistAdminQuery />);
};
