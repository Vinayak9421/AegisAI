import { useState, useEffect } from 'react';
import SideNavBar from './SideNavBar';
import TopNavBar from './TopNavBar';

export default function AppLayout({ children, pageTitle }) {
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem('aegis_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const [mobileOpen, setMobileOpen] = useState(false);

  const toggleCollapse = () => {
    setCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('aegis_sidebar_collapsed', String(next));
      } catch {
        // ignore
      }
      return next;
    });
  };

  const toggleMobile = () => {
    setMobileOpen((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex">
      {/* Persistent Collapsible Side Navigation Bar */}
      <SideNavBar
        collapsed={collapsed}
        onToggleCollapse={toggleCollapse}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out print:ml-0 ${
          collapsed ? 'md:ml-[76px]' : 'md:ml-[260px]'
        }`}
      >
        {/* Top Header - No shifting navigation items */}
        <div className="print:hidden">
          <TopNavBar
            collapsed={collapsed}
            onToggleCollapse={toggleCollapse}
            onToggleMobile={toggleMobile}
            pageTitle={pageTitle}
          />
        </div>

        {/* Dynamic Page Container */}
        <main className="flex-1 p-5 md:p-8 max-w-[1500px] w-full mx-auto print:p-0 print:max-w-none">
          {children}
        </main>
      </div>
    </div>
  );
}
