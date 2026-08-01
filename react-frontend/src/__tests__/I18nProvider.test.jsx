import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { I18nProvider, useI18n } from "../i18n";

function TestComponent() {
  const { t, locale, setLocale } = useI18n();
  return (
    <div>
      <p data-testid="greeting">{t("greeting")}</p>
      <p data-testid="interpolated">{t("interpolated", { name: "Mundo" })}</p>
      <p data-testid="locale">{locale}</p>
      <button onClick={() => setLocale("fil")}>Switch to Filipino</button>
    </div>
  );
}

function renderWithI18n() {
  return render(
    <I18nProvider>
      <TestComponent />
    </I18nProvider>
  );
}

describe("I18nProvider", () => {
  it("defaults to English", () => {
    renderWithI18n();
    expect(screen.getByTestId("locale")).toHaveTextContent("en");
    expect(screen.getByTestId("greeting")).toHaveTextContent("Hello");
  });

  it("interpolates placeholders", () => {
    renderWithI18n();
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Hello, Mundo");
  });

  it("switches to Filipino", () => {
    renderWithI18n();
    fireEvent.click(screen.getByText("Switch to Filipino"));
    expect(screen.getByTestId("locale")).toHaveTextContent("fil");
    expect(screen.getByTestId("greeting")).toHaveTextContent("Kamusta");
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Kamusta, Mundo");
  });

  it("falls back to English for missing Filipino keys", () => {
    renderWithI18n();
    fireEvent.click(screen.getByText("Switch to Filipino"));
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Kamusta, Mundo");
  });
});
