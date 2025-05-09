import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="layout">
      <nav class="navbar">
        <div class="navbar-brand">
          <div class="logo">
            <i class="fas fa-shield-virus"></i>
            <span>Mask Detector</span>
          </div>
        </div>
        <div class="navbar-menu">
          <a routerLink="/video" routerLinkActive="active" class="nav-item">
            <i class="fas fa-video"></i>
            <span>Video Stream</span>
          </a>
          <a routerLink="/stats" routerLinkActive="active" class="nav-item">
            <i class="fas fa-chart-bar"></i>
            <span>Statistics</span>
          </a>
          <a routerLink="/history" routerLinkActive="active" class="nav-item">
            <i class="fas fa-history"></i>
            <span>History</span>
          </a>
          <a routerLink="/time" routerLinkActive="active" class="nav-item">
            <i class="fas fa-clock"></i>
            <span>Time Stats</span>
          </a>
        </div>
      </nav>
      <main class="main-content">
        <ng-content></ng-content>
      </main>
    </div>
  `,
  styles: [`
    .layout {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      background: #f8f9fa;
    }
    .navbar {
      background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .navbar-brand {
      color: white;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      font-size: 1.5rem;
      font-weight: bold;
    }
    .logo i {
      font-size: 1.8rem;
      background: rgba(255,255,255,0.2);
      padding: 0.5rem;
      border-radius: 50%;
      box-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    .logo span {
      text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .navbar-menu {
      display: flex;
      gap: 1.5rem;
    }
    .nav-item {
      color: rgba(255,255,255,0.9);
      text-decoration: none;
      padding: 0.7rem 1.2rem;
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 0.8rem;
      transition: all 0.3s ease;
      font-weight: 500;
    }
    .nav-item:hover {
      background: rgba(255,255,255,0.15);
      transform: translateY(-2px);
    }
    .nav-item.active {
      background: rgba(255,255,255,0.2);
      color: white;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .nav-item i {
      font-size: 1.2rem;
    }
    .main-content {
      flex: 1;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }
  `]
})
export class LayoutComponent {}
