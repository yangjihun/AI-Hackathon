import type {
  CharacterCardResponse,
  Episode,
  GraphResponse,
  QARequest,
  QAResponse,
  RecapRequest,
  RecapResponse,
  Title,
  UUID,
} from "../types/netplus";
import { apiRequest } from "./http";

interface PaginatedTitlesResponse {
  items: Title[];
  next_cursor: string | null;
}

interface EpisodesResponse {
  title_id: UUID;
  episodes: Episode[];
}

function toQuery(params: Record<string, string | number | boolean | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined) {
      continue;
    }
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function listTitles(): Promise<Title[]> {
  const response = await apiRequest<PaginatedTitlesResponse>("/api/titles");
  return response.items.map((item) => ({
    ...item,
    description: item.description ?? "",
  }));
}

export async function listEpisodes(titleId: UUID): Promise<Episode[]> {
  const response = await apiRequest<EpisodesResponse>(`/api/titles/${titleId}/episodes`);
  return response.episodes.map((episode) => ({
    ...episode,
    name: episode.name ?? `Episode ${episode.episode_number}`,
    duration_ms: episode.duration_ms ?? 0,
  }));
}

export async function getGraph(params: {
  title_id: UUID;
  episode_id: UUID;
  current_time_ms: number;
}): Promise<GraphResponse> {
  const query = toQuery({
    title_id: params.title_id,
    episode_id: params.episode_id,
    current_time_ms: params.current_time_ms,
  });
  return apiRequest<GraphResponse>(`/api/graph${query}`);
}

export async function createRecap(params: RecapRequest): Promise<RecapResponse> {
  return apiRequest<RecapResponse>("/api/recap", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function askQuestion(params: QARequest): Promise<QAResponse> {
  return apiRequest<QAResponse>("/api/qa", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function getCharacterCard(params: {
  character_id: UUID;
  episode_id: UUID;
  current_time_ms: number;
}): Promise<CharacterCardResponse> {
  const query = toQuery({
    episode_id: params.episode_id,
    current_time_ms: params.current_time_ms,
  });
  return apiRequest<CharacterCardResponse>(`/api/characters/${params.character_id}${query}`);
}
