import AppLayout from './AppLayout';

export default function AdminLayout({ children, pageTitle }) {
  return <AppLayout pageTitle={pageTitle}>{children}</AppLayout>;
}
