import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../services/websocket.service';

@Component({
  selector: 'app-time',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="time-container">
      <h2>Time Statistics</h2>
      <div class="time-grid">
        <div class="time-card">
          <h3>Average Time With Mask</h3>
          <p>{{ avgTimeWithMask }} seconds</p>
        </div>
        <div class="time-card">
          <h3>Average Time Without Mask</h3>
          <p>{{ avgTimeWithoutMask }} seconds</p>
        </div>
        <div class="time-card">
          <h3>Total Time Monitored</h3>
          <p>{{ totalTime }} seconds</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .time-container {
      padding: 20px;
    }
    .time-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    .time-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .time-card h3 {
      margin: 0;
      color: #666;
      font-size: 1rem;
    }
    .time-card p {
      margin: 10px 0 0;
      font-size: 2rem;
      font-weight: bold;
      color: #333;
    }
  `]
})
export class TimeComponent implements OnInit {
  avgTimeWithMask = 0;
  avgTimeWithoutMask = 0;
  totalTime = 0;

  constructor(private wsService: WebSocketService) {}

  ngOnInit() {
    this.wsService.connect().subscribe({
      next: (data) => {
        if (data.type === 'time_stats') {
          this.avgTimeWithMask = data.avg_time_with_mask;
          this.avgTimeWithoutMask = data.avg_time_without_mask;
          this.totalTime = data.total_time;
        }
      }
    });
  }
}
