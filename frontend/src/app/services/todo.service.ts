import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, tap } from 'rxjs';
import { Todo, TodoCreateDTO, TodoUpdateDTO, TodoResponse, TodosResponse } from '../models/todo.interface';
// import { environment } from '../../environments/environment';
import { ErrorService } from './error.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TodoService {
  private apiUrl = `${environment.apiUrl}/todos`;

  constructor(
    private http: HttpClient,
    private errorService: ErrorService
  ) {}

  getTodos(): Observable<TodosResponse> {
    return this.http.get<TodosResponse>(this.apiUrl)
      .pipe(
        catchError(error => {
          this.errorService.handleError(error);
          throw error;
        })
      );
  }

  getTodoById(id: string): Observable<TodoResponse> {
    return this.http.get<TodoResponse>(`${this.apiUrl}/${id}`)
      .pipe(
        catchError(error => {
          this.errorService.handleError(error);
          throw error;
        })
      );
  }

  createTodo(todo: TodoCreateDTO): Observable<TodoResponse> {
    return this.http.post<TodoResponse>(this.apiUrl, todo)
      .pipe(
        catchError(error => {
          this.errorService.handleError(error);
          throw error;
        })
      );
  }

  updateTodo(todoData: TodoUpdateDTO): Observable<Todo> {
    const url = `${this.apiUrl}/${todoData.id}`;
    // Remove the id from the payload since it's in the URL
    const { id, ...updateData } = todoData;
    
    return this.http.put<Todo>(url, updateData).pipe(
      tap(updatedTodo => {
        console.log('Todo updated:', updatedTodo);
      }),
      catchError(error => {
        console.error('Error updating todo:', error);
        throw error;
      })
    );
  }

  deleteTodo(id: string): Observable<TodoResponse> {
      return this.http.delete<TodoResponse>(`${this.apiUrl}/${id}`)

        .pipe(
          tap(response => {
            console.log('Delete todo response:', response);
          }),
          catchError(error => {
            this.errorService.handleError(error);
            throw error;
          })
        );
    
  }
} 