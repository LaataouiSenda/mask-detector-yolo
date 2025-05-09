import { Routes } from '@angular/router';
import { VideoComponent } from './components/video/video.component';
import { StatsComponent } from './components/stats/stats.component';
import { HistoryComponent } from './components/history/history.component';
import { TimeComponent } from './components/time/time.component';

export const routes: Routes = [
  { path: '', redirectTo: 'video', pathMatch: 'full' },
  { path: 'video', component: VideoComponent },
  { path: 'stats', component: StatsComponent },
  { path: 'history', component: HistoryComponent },
  { path: 'time', component: TimeComponent }
];
