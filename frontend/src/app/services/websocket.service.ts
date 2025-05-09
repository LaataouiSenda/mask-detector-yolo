import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { Observable, Subject, timer } from 'rxjs';
import { retryWhen, tap, delayWhen } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket$: WebSocketSubject<any> | undefined;
  private messagesSubject = new Subject<any>();
  public messages$ = this.messagesSubject.asObservable();
  private reconnectInterval = 2000; // 2 seconds

  constructor() {
    console.log('WebSocket service initialized');
    this.initializeConnection();
  }

  private initializeConnection(): void {
    console.log('Initializing WebSocket connection');
    if (!this.socket$ || this.socket$.closed) {
      console.log('Creating new WebSocket connection');
      this.socket$ = webSocket({
        url: 'ws://localhost:5000/ws',
        openObserver: {
          next: () => {
            console.log('WebSocket connected successfully');
          }
        },
        closeObserver: {
          next: () => {
            console.log('WebSocket disconnected, attempting to reconnect...');
            this.socket$ = undefined;
            this.initializeConnection();
          }
        }
      });

      this.socket$.pipe(
        retryWhen(errors =>
          errors.pipe(
            tap(err => console.error('WebSocket error, retrying:', err)),
            delayWhen(() => timer(this.reconnectInterval))
          )
        )
      ).subscribe(
        message => {
          console.log('WebSocket message received:', message);
          if (message && message.data) {
            this.messagesSubject.next({
              type: 'frame',
              frame: message.data
            });
          }
        },
        err => console.error('WebSocket error:', err),
        () => console.log('WebSocket connection closed')
      );
    }
  }

  connect(): Observable<any> {
    console.log('Connect method called');
    return this.messages$;
  }

  sendMessage(message: any): void {
    if (this.socket$) {
      console.log('Sending message:', message);
      this.socket$.next(message);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  }

  close(): void {
    if (this.socket$) {
      console.log('Closing WebSocket connection');
      this.socket$.complete();
    }
  }
}
