import { Routes } from '@angular/router';
import { TodoListComponent } from './components/todo-list/todo-list.component';
import { NewtestComponent } from './components/newtest/newtest.component';

export const routes: Routes = [
  { path: '', component: TodoListComponent },
  { path: 'test', component: NewtestComponent },
  { path: '**', component: TodoListComponent }, // Catch all route
];
