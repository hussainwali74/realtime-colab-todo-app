import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class ErrorService {
    constructor(private snackBar: MatSnackBar) { }

    handleError(error: Error | HttpErrorResponse | string) {
        let errorMessage: string;

        if (typeof error === 'string') {
            errorMessage = error;
        } else if (error instanceof HttpErrorResponse) {
            // Handle HTTP errors
            errorMessage = error.error?.message || error.message || 'An HTTP error occurred';
        } else {
            // Handle general errors
            errorMessage = error.message || 'An unexpected error occurred';
        }

        console.error('Error:', error);
        this.showError(errorMessage);
    }

    private showError(message: string) {
        this.snackBar.open(message, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'bottom',
            panelClass: ['error-snackbar']
        });
    }

    showSuccess(message: string): void {
        this.snackBar.open(message, 'Close', {
            duration: 3000,
            horizontalPosition: 'end',
            verticalPosition: 'bottom',
            panelClass: ['success-snackbar']
        });
    }
} 