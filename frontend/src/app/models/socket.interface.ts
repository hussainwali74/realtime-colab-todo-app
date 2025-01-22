import { Todo } from "./todo.interface";

export enum SocketEvent {
  CONNECT = 'connect',
  DISCONNECT = 'disconnect',
  TODO_CREATED = 'todo_created',
  TODO_UPDATED = 'todo_updated',
  TODO_DELETED = 'todo_deleted',
  ERROR = 'error'
}

export interface SocketMessage<T = any> {
  event: SocketEvent;
  data: T;
  timestamp: number;
}

export interface TodoSocketEvent {
  todoId: string;
  action: 'create' | 'update' | 'delete';
  data?: Todo;
  version?: number;
}

export interface SocketError {
  code: string;
  message: string;
} 