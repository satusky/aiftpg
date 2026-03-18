import { AppShell, Group, Title, Anchor } from '@mantine/core';
import { Outlet, Link } from 'react-router-dom';

export default function Layout() {
  return (
    <AppShell header={{ height: 56 }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md">
          <Anchor component={Link} to="/" underline="never">
            <Title order={3}>Hackathon Dashboard</Title>
          </Anchor>
        </Group>
      </AppShell.Header>
      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
