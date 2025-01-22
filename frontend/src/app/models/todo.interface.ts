export interface Todo {
  id?: string;
  _id?: string;
  title: string;
  description: string;
  completed: boolean;
  created_at?: Date;
  updated_at?: Date;
  version?: number; // For handling concurrent updates
}

export interface TodoCreateDTO {
  title: string;
  description: string;
}

export interface TodoUpdateDTO {
  id: string;
  title?: string;
  description?: string;
  completed?: boolean;
  version?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface TodosResponse extends ApiResponse<Todo[]> {}
export interface TodoResponse extends ApiResponse<Todo> {} 