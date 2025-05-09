import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../services/websocket.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="history-container">
      <h2>Detection History</h2>
      <div class="history-list">
        <div class="history-item" *ngFor="let item of history">
          <div class="time">{{ item.timestamp | date:'medium' }}</div>
          <div class="status" [class.warning]="!item.with_mask">
            {{ item.with_mask ? 'With Mask' : 'Without Mask' }}
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .history-container {
      padding: 20px;
    }
    .history-list {
      margin-top: 20px;
    }
    .history-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px;
      background: white;
      border-radius: 8px;
      margin-bottom: 10px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .time {
      color: #666;
    }
    .status {
      padding: 5px 10px;
      border-radius: 4px;
      background: #4CAF50;
      color: white;
    }
    .status.warning {
      background: #f44336;
    }
  `]
})
export class HistoryComponent implements OnInit {
  history: any[] = [];

  constructor(private wsService: WebSocketService) {}

  ngOnInit() {
    this.wsService.connect().subscribe({
      next: (data) => {
        if (data.type === 'history') {
          this.history = data.history;
        }
      }
    });
  }
}
