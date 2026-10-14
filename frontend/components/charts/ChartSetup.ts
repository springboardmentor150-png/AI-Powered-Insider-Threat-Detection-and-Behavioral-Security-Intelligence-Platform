"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

let registered = false;

export function registerChartJS() {
  if (typeof window !== "undefined" && !registered) {
    ChartJS.register(
      CategoryScale,
      LinearScale,
      BarElement,
      PointElement,
      LineElement,
      ArcElement,
      Title,
      Tooltip,
      Legend,
      Filler
    );
    registered = true;
  }
}

registerChartJS();
