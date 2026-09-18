import { describe, it, expect, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { I18nProvider } from "../../i18n";
import EcosimWizard from "../ecosim/EcosimWizard";

function setup(overrides = {}) {
  const props = {
    mode: "municipality",
    setMode: vi.fn(),
    muniQuery: "",
    setMuniQuery: vi.fn(),
    muniOpen: false,
    setMuniOpen: vi.fn(),
    filteredMunicipalities: [],
    municipalityId: "",
    setMunicipalityId: vi.fn(),
    municipalitiesError: null,
    provinceQuery: "",
    setProvinceQuery: vi.fn(),
    provinceOpen: false,
    setProvinceOpen: vi.fn(),
    filteredProvinces: [],
    provinceId: "",
    setProvinceId: vi.fn(),
    provincesError: null,
    monthlyConsumption: 0,
    setMonthlyConsumption: vi.fn(),
    monthlyBill: 0,
    setMonthlyBill: vi.fn(),
    electricityRate: 0,
    setElectricityRate: vi.fn(),
    desiredSavings: 50,
    setDesiredSavings: vi.fn(),
    includeAi: false,
    setIncludeAi: vi.fn(),
    onRun: vi.fn(),
    loading: false,
    activeId: null,
    result: null,
    user: null,
    onSave: vi.fn(),
    onDownloadPdf: vi.fn(),
    downloadPdfLoading: false,
    ...overrides,
  };
  render(
    <I18nProvider>
      <EcosimWizard {...props} />
    </I18nProvider>
  );
  return props;
}

describe("EcosimWizard", () => {
  it("renders step 1 of 5", () => {
    setup();
    expect(screen.getByText("Step 1 of 5")).toBeInTheDocument();
  });

  it("hides the province mode toggle", () => {
    setup();
    expect(screen.queryByText("Province")).not.toBeInTheDocument();
  });
});

describe("EcosimWizard Save as PDF gating", () => {
  const goToStep5 = () => {
    for (let i = 0; i < 4; i++) {
      fireEvent.click(screen.getByText("Next"));
    }
    expect(screen.getByText("Step 5 of 5")).toBeInTheDocument();
  };

  const stepProps = {
    activeId: "1",
    monthlyConsumption: 350,
    monthlyBill: 5000,
    electricityRate: 14,
    result: {},
  };

  it("hides Save as PDF while AI analysis is still generating", () => {
    setup({ ...stepProps, includeAi: true, aiLoading: true });
    goToStep5();
    expect(screen.queryByText("Save as PDF")).not.toBeInTheDocument();
  });

  it("shows Save as PDF once the AI summary has resolved", () => {
    setup({
      ...stepProps,
      includeAi: true,
      aiLoading: false,
      result: { ai_analysis: { summary: "Analysis text" } },
    });
    goToStep5();
    expect(screen.getByText("Save as PDF")).toBeInTheDocument();
  });

  it("hides Save as PDF when ai_analysis reports a pending status", () => {
    setup({
      ...stepProps,
      includeAi: true,
      aiLoading: false,
      result: { ai_analysis: { status: "pending", summary: "pending text" } },
    });
    goToStep5();
    expect(screen.queryByText("Save as PDF")).not.toBeInTheDocument();
  });

  it("shows Save as PDF when AI analysis failed", () => {
    setup({ ...stepProps, includeAi: true, aiLoading: false, aiError: "AI failed" });
    goToStep5();
    expect(screen.getByText("Save as PDF")).toBeInTheDocument();
  });

  it("shows Save as PDF immediately when AI is not included", () => {
    setup({ ...stepProps, includeAi: false });
    goToStep5();
    expect(screen.getByText("Save as PDF")).toBeInTheDocument();
  });
});
