import SideNavBar from './SideNavBar';

export default function AdminLayout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <SideNavBar />
      <main className="flex-1 md:ml-[280px] flex flex-col h-screen overflow-hidden bg-background">
        {children}
      </main>
    </div>
  );
}
