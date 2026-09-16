import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
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
