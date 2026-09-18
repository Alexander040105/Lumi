import { supabase } from "./supabaseClient";

export async function saveLocation({ userId, municipalityId, label }) {
  const { data: row, error } = await supabase
    .from("saved_locations")
    .insert({ user_id: userId, municipality_id: municipalityId, label })
    .select()
    .single();

  if (error) {
    if (error.code === "23505" || error.status === 409) {
      return { status: "duplicate" };
    }
    return { status: "error", error };
  }
  return { status: "saved", row };
}
