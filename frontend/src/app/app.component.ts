import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Mask Detection System';
  videoUrl = 'http://localhost:5000/video_feed';
  
  // Statistics
  withMaskCount = 0;
  withoutMaskCount = 0;
  incorrectMaskCount = 0;
  
  // Update statistics from detection results
  updateStats(stats: any) {
    this.withMaskCount = stats.with_mask || 0;
    this.withoutMaskCount = stats.without_mask || 0;
    this.incorrectMaskCount = stats.mask_weared_incorrect || 0;
  }
} 