import pandas as pd

electorates = ["brindabella", "ginninderra", "kurrajong", "murrumbidgee", "yerrabi"]

# empty dataframe to store all preference data
final_flows = pd.DataFrame()

# iterate through the electorates
for i, electorate in enumerate(electorates):

    # read preference data (from Electoral Commission)
    data = pd.read_excel(f"https://www.elections.act.gov.au/elections_and_voting/2020_legislative_assembly_election/distribution-of-preferences-2020/table2_{electorate}.xlsx")

    # establish quota
    quota = data.columns[list(data.columns).index("Quota = ") + 1]
    electorates[i] = [electorate, quota]

    # read in data again, trim and transform it
    data = pd.read_excel(f"https://www.elections.act.gov.au/elections_and_voting/2020_legislative_assembly_election/distribution-of-preferences-2020/table2_{electorate}.xlsx", header=1).T.iloc[1:]

    # establish candidates
    candidates = data[0].dropna().apply(lambda x: x.strip())
    rawParties = candidates.index
    candidates = list(candidates)

    # build parties list
    parties = []
    party = 0
    for index, candidate in enumerate(candidates):
        if "Unnamed" not in rawParties[index]:
            party = index
        parties.append(rawParties[party])

    # empty dataframe for this electorate's preference flows
    electorate_flows = pd.DataFrame(data=parties, index=candidates, columns=["party"])
    electorate_flows.index.name = "candidate"
    electorate_flows.loc["exhausted"] = "nan"
    electorate_flows.loc["comment"] = "nan"
    results = []
    data.set_index(0, inplace=True)
    new_index = []
    for indice in list(data.index):
        if indice == indice:
            new_index.append(indice.strip())
        else:
            new_index.append(indice)
    data.index = new_index

    # iterate through candidates
    for candidate in candidates + ["exhausted", "comment"]:
        array = []
        for j, column in enumerate(data.columns):
            if data.iloc[-2, j] == data.iloc[-2, j]:
                if candidate not in ["exhausted", "comment"]:
                    array.append(data.loc[candidate, column])
                elif candidate == "exhausted":
                    array.append(data.iloc[-4, j])
                elif candidate == "comment":
                    array.append(data.iloc[-1, j])
        results.append(array)

    electorate_flows["counts"] = results
    electorate_flows["electorate"] = len(electorate_flows) * [electorate]

    # append electorate flows to combined dataframe
    final_flows = pd.concat([final_flows, electorate_flows])

# create two files: preference data and electorate data
electorate_flows.to_csv("preferences.csv")
electorates = pd.DataFrame(electorates)
electorates.columns = ["electorate", "quota"]
electorates.to_csv("electorates.csv", index=False)
