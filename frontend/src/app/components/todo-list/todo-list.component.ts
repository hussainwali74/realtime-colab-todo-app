import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TodoFormComponent } from '../todo-form/todo-form.component';
import { TodoService } from '../../services/todo.service';
import { WebSocketService } from '../../services/websocket.service';
import {
  Todo,
  TodoCreateDTO,
  TodoUpdateDTO,
} from '../../models/todo.interface';
import { SocketEvent } from '../../models/socket.interface';
import { Subject, takeUntil } from 'rxjs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ErrorService } from '../../services/error.service';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { TodoEditDialogComponent } from '../todo-edit-dialog/todo-edit-dialog.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-todo-list',
  standalone: true,
  imports: [
    CommonModule,
    TodoFormComponent,
    MatProgressSpinnerModule,
    MatCheckboxModule,
    MatIconModule,
    MatButtonModule,
    MatSnackBarModule,
    MatDialogModule,
    TodoEditDialogComponent,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './todo-list.component.html',
  styleUrls: ['./todo-list.component.scss'],
})
export class TodoListComponent implements OnInit, OnDestroy {
  todos = signal<Todo[]>([]);
  loading = true;
  onlineUsers: number = 0;
  private destroy$ = new Subject<void>();
  searchTerm: string = '';
  private allTodos: Todo[] = [];
  statusFilter: 'all' | 'active' | 'completed' = 'all';

  constructor(
    private todoService: TodoService,
    private wsService: WebSocketService,
    private errorService: ErrorService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadTodos();
    this.setupWebSocket();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.wsService.disconnect();
  }

  private loadTodos(): void {
    this.todoService
      .getTodos()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('Todos loaded:', response);
          this.allTodos = Array.isArray(response) ? response : [];
          if (this.allTodos.length > 0) {
            this.allTodos = this.sortTodos(this.allTodos);
          }
          this.filterTodos();
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading todos:', error);
          this.loading = false;
          this.errorService.handleError('Failed to load todos');
        },
      });
  }

  private sortTodos(todos: Todo[]): Todo[] {
    return todos.sort((a, b) => {
      return (
        new Date(b.created_at!).getTime() - new Date(a.created_at!).getTime()
      );
    });
  }

  private setupWebSocket(): void {
    console.log('Setting up WebSocket connections...');
    this.wsService.connect();

    this.wsService
      .onUserCount()
      .pipe(takeUntil(this.destroy$))
      .subscribe((count) => {
        this.onlineUsers = count;
      });

    // Listen for todo created events
    console.log('Subscribing to todo created events...');
    this.wsService
      .onTodoEvent(SocketEvent.TODO_CREATED)
      .pipe(takeUntil(this.destroy$))
      .subscribe((event) => {
        if (event.data) {
          this.allTodos = [...this.allTodos, event.data];
          this.filterTodos();
          this.todos.set(this.sortTodos(this.allTodos));
        }
      });

    // Listen for todo updated events
    console.log('Subscribing to todo updated events...');
    this.wsService
      .onTodoEvent(SocketEvent.TODO_UPDATED)
      .pipe(takeUntil(this.destroy$))
      .subscribe((event) => {
        if (event.data) {
          this.allTodos = this.allTodos.map((todo) =>
            todo._id === event.data!._id ? event.data! : todo
          );
          this.filterTodos();
          this.todos.set(this.sortTodos(this.allTodos));
        }
      });

    // Listen for todo deleted events
    console.log('Subscribing to todo deleted events...');
    this.wsService
      .onTodoEvent(SocketEvent.TODO_DELETED)
      .pipe(takeUntil(this.destroy$))
      .subscribe((event) => {
        if (event.data?._id) {
          this.allTodos = this.allTodos.filter(
            (todo) => todo._id !== event.data!._id
          );
          this.filterTodos();
          this.todos.set(this.sortTodos(this.allTodos));
        }
      });
  }

  onCreateTodo(todoData: TodoCreateDTO): void {
    this.todoService
      .createTodo(todoData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('Create todo response:', response);
          if (response && response.data) {
            // this.todos.update(todos => [...todos, response.data]);
            // this.todos.set(this.sortTodos([...this.todos(), response.data]));

            this.errorService.showSuccess('Todo created successfully');
          }
        },
        error: (error) => {
          console.error('Error creating todo:', error);
          this.errorService.handleError('Failed to create todo');
        },
      });
  }

  onUpdateTodo(todoData: TodoUpdateDTO): void {
    this.todoService
      .updateTodo(todoData)
      .pipe(takeUntil(this.destroy$))
      .subscribe();
  }

  onDeleteTodo(todo: Todo): void {
    const todoId = todo._id;
    if (!todoId) {
      this.errorService.handleError('Invalid todo ID');
      return;
    }

    this.todoService
      .deleteTodo(todoId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('Delete todo response:', response);
          // Local state update will happen through WebSocket event
          this.errorService.showSuccess('Todo deleted successfully');
        },
        error: (error) => {
          console.error('Error deleting todo:', error);
          this.errorService.handleError('Failed to delete todo');
        },
      });
  }

  onEdit(todo: Todo): void {
    const dialogRef = this.dialog.open(TodoEditDialogComponent, {
      data: { ...todo },
    });

    dialogRef
      .afterClosed()
      .pipe(takeUntil(this.destroy$))
      .subscribe((result) => {
        if (result) {
          const updateData: TodoUpdateDTO = {
            id: todo._id!,
            title: result.title,
            description: result.description,
          };

          this.todoService
            .updateTodo(updateData)
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (updatedTodo) => {
                console.log('Todo edited:', updatedTodo);
                this.errorService.showSuccess('Todo edited successfully');
              },
              error: (error) => {
                console.error('Error editing todo:', error);
                this.errorService.handleError('Failed to edit todo');
              },
            });
        }
      });
  }

  onStatusChange(todo: Todo): void {
    const updateData: TodoUpdateDTO = {
      id: todo._id!,
      completed: !todo.completed, // Toggle the status
    };

    console.log('Status change for todo:', todo);
    console.log('updateData', updateData);
    // return
    this.todoService
      .updateTodo(updateData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (updatedTodo) => {
          console.log('Todo status updated:', updatedTodo);
          // Update the local state
          this.todos.update((todos) =>
            todos.map((t) => (t._id === updatedTodo._id ? updatedTodo : t))
          );
          this.errorService.showSuccess('Todo status updated successfully');
        },
        error: (error) => {
          console.error('Error updating todo status:', error);
          this.errorService.handleError('Failed to update todo status');
          // Revert the checkbox state in case of error
          todo.completed = !todo.completed;
        },
      });
  }

  onSearch(term: string): void {
    this.filterTodos();
  }

  filterTodos(): void {
    let filtered = [...this.allTodos];

    // Apply search filter
    if (this.searchTerm.trim()) {
      const searchTerm = this.searchTerm.toLowerCase().trim();
      filtered = filtered.filter(
        (todo) =>
          todo.title.toLowerCase().includes(searchTerm) ||
          todo.description.toLowerCase().includes(searchTerm)
      );
    }

    // Apply status filter
    if (this.statusFilter !== 'all') {
      filtered = filtered.filter((todo) =>
        this.statusFilter === 'completed' ? todo.completed : !todo.completed
      );
    }

    this.todos.set(filtered);
  }
}
