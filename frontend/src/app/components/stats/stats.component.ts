import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../services/websocket.service';

@Component({
  selector: 'app-stats',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="stats-container">
      <h2>Statistics</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Total Detections</h3>
          <p>{{ totalDetections }}</p>
        </div>
        <div class="stat-card">
          <h3>With Mask</h3>
          <p>{{ withMask }}</p>
        </div>
        <div class="stat-card">
          <h3>Without Mask</h3>
          <p>{{ withoutMask }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .stats-container {
      padding: 20px;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-card h3 {
      margin: 0;
      color: #666;
      font-size: 1rem;
    }
    .stat-card p {
      margin: 10px 0 0;
      font-size: 2rem;
      font-weight: bold;
      color: #333;
    }
  `]
})
export class StatsComponent implements OnInit {
  totalDetections = 0;
  withMask = 0;
  withoutMask = 0;

  constructor(private wsService: WebSocketService) {}

  ngOnInit() {
    this.wsService.connect().subscribe({
      next: (data) => {
        if (data.type === 'stats') {
          this.totalDetections = data.total;
          this.withMask = data.with_mask;
          this.withoutMask = data.without_mask;
        }
      }
    });
  }
}
