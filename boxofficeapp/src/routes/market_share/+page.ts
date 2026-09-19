import { redirect } from "@sveltejs/kit";

export const load = async ({ params }) => {
    // get the current year
    const currentYear = new Date().getFullYear();

    redirect(302, `/market_share/numbers_genre/${currentYear}-01-01/${currentYear}-12-31`);
};