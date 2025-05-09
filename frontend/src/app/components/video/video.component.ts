import { Component } from '@angular/core';

@Component({
  selector: 'app-video',
  standalone: true,
  template: `
    <div class="video-page">
      <div class="video-header">
        <h2>Live Video Stream</h2>
        <div class="status-indicator connected">
          <i class="fas fa-circle"></i>
          Connected
        </div>
      </div>
      <div class="video-frame">
        <div class="video-container">
          <img src="http://localhost:5000/test_camera" alt="Video Stream" style="width:100%;height:100%;object-fit:cover;" />
        </div>
      </div>
    </div>
  `,
  styles: [`
    .video-page { max-width: 1200px; margin: 0 auto; }
    .video-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
    .video-header h2 { color: #2c3e50; margin: 0; font-size: 1.8rem; font-weight: 600; }
    .status-indicator { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 20px; background: #2ecc71; color: white; font-size: 0.9rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .status-indicator.connected { background: #2ecc71; }
    .video-frame { background: #fff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; aspect-ratio: 16/9; }
    .video-container { position: relative; width: 100%; height: 100%; }
    img { width: 100%; height: 100%; object-fit: cover; }
  `]
})
export class VideoComponent {}
