import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';
import { environment } from '../../environments/environment';
import {
  SocketEvent,
  SocketMessage,
  TodoSocketEvent,
  SocketError,
} from '../models/socket.interface';
import { ErrorService } from './error.service';

@Injectable({
  providedIn: 'root',
})
export class WebSocketService {
  private socket: Socket;
  private connected$ = new BehaviorSubject<boolean>(false);

  constructor(private errorService: ErrorService) {
    console.log('WebSocketService constructor - URL:', environment.wsUrl);

    this.socket = io(environment.wsUrl, {
      transports: ['polling', 'websocket'], // Start with polling, upgrade to websocket
      autoConnect: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      path: '/socket.io/',
      withCredentials: true,
      forceNew: true,
      timeout: 60000,
    });

    console.log('WebSocketService socket instance:', this.socket);
    this.setupSocketListeners();
  }

  private setupSocketListeners(): void {
    this.socket.on('connect', () => {
      console.log('Socket connected with ID:', this.socket.id);
      this.connected$.next(true);
    });

    this.socket.on('connection_status', (data: any) => {
      console.log('Connection status received:', data);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
      this.connected$.next(false);
      this.errorService.handleError(
        'Connection to server lost. Attempting to reconnect...'
      );
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.errorService.handleError(
        'Failed to connect to server. Please check your connection.'
      );
    });

    this.socket.onAny((event, ...args) => {
      console.log('Socket event:', event, 'Data:', args);
    });
  }

  connect(): void {
    if (!this.socket.connected) {
      this.socket.connect();
    }
  }

  disconnect(): void {
    if (this.socket.connected) {
      this.socket.disconnect();
    }
  }

  isConnected(): Observable<boolean> {
    return this.connected$.asObservable();
  }

  onTodoEvent(event: SocketEvent): Observable<TodoSocketEvent> {
    console.log(`Setting up listener for event: ${event}`);
    return new Observable((observer) => {
      this.socket.on(event, (data: TodoSocketEvent) => {
        console.log(`Received ${event} event:`, data);
        try {
          observer.next(data);
        } catch (error) {
          console.error(`Error processing ${event} event:`, error);
          this.errorService.handleError('Error processing todo event');
          observer.error(error);
        }
      });

      // Log when subscription is created
      console.log(`Subscribed to ${event} events`);

      return () => {
        console.log(`Unsubscribing from ${event} events`);
        this.socket.off(event);
      };
    });
  }

  emit(event: SocketEvent, data: any): void {
    if (!this.socket.connected) {
      this.errorService.handleError('Not connected to server');
      return;
    }

    try {
      this.socket.emit(event, data);
    } catch (error) {
      this.errorService.handleError('Failed to send data to server');
      throw error;
    }
  }

  onUserCount(): Observable<number> {
    return new Observable((observer) => {
      this.socket.on('user_count', (count: number) => {
        console.log('Raw user count received:', count);
        observer.next(count);
      });

      return () => {
        this.socket.off('user_count');
      };
    });
  }
}
