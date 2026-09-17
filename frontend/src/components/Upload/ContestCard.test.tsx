import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import '../../i18n/config';
import { contest } from '../../test/fixtures';
import ContestCard from './ContestCard';

describe('contest information', () => {
  it('shows the contest and opens its upload route', () => {
    render(
      <MemoryRouter>
        <ContestCard contest={contest} />
      </MemoryRouter>,
    );
    expect(
      screen.getByRole('heading', { name: contest.title }),
    ).toBeInTheDocument();
    expect(screen.getByText(contest.description ?? '')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /open/i })).toHaveAttribute(
      'href',
      '/contest/1/upload',
    );
    expect(screen.getByRole('img')).toHaveAttribute('alt', contest.title);
  });
});
