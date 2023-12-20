class CP_Child:
    """
    --------------------
    Attributes from dictionary
    --------------------
    id : int
        child id

    age : int
        age (0-5)

    family : int = Family.id

    initial_daycare : int = Daycare.id

    actual_daycare : int = Daycare.id

    pref : list[int]

    --------------------
    Additional Attributes
    --------------------
    projected_preference_id_list : list[int]
        induced from family.pref later

    all_daycare_ids : list[int]
        induced from self.projected_preference_id_list

    assigned_daycare_id : int = Daycare.id
        assignment by CP algorithm
    """

    def __init__(
        self,
        c_id: int,
        age: int,
        family_id: int,
        initial_daycare_id: int,
        actual_daycare_id: int,
        preference_list: list[int],
    ):
        # attributes from dictionary
        self.id = c_id
        self.age = age
        self.family = family_id
        self.initial_daycare = initial_daycare_id
        self.actual_daycare = actual_daycare_id
        self.pref = [
            d_id if d_id is not None else 9999 for d_id in preference_list
        ]  # replace None with 9999
        # additional attributes
        self.projected_pref = []
        self.all_daycare_ids = []  # notation D(\succ_c)
        self.assigned_daycare = None

    def __str__(self):
        return f"child {self.id}"

    def __repr__(self):
        return f"child {self.id}"

    # notation P(c, d)
    def return_all_positions_of_certain_dacyare_in_projected_pref(self, daycare_id):
        """
        return a list of positions corresonding to daycare_id in self.projected_pref
        """
        positions = []
        for index, d_id in enumerate(self.projected_pref):
            if d_id == daycare_id and index not in positions:
                positions.append(index)
        return positions


class CP_Daycare:
    """

    Attributes from Dictionary
    ----------
    id: int
        a dummy daycare with id=9999 representing the option of being unmatched for children

    recruiting_numbers_list: list[int]
        the number of recruiting children by age, where each position represents one age

    share_ages_list: list[list[int]]
        a list of lists of ages s.t. children from the same list can share recruiting_numbers
        e.g., [[0,1],[4,5]] indicating that age 0 and 1 can share room, age 4 and 5 can share room

    priority_child_id_list: list[child.id: int]
        priority list of each daycare

    priority_score_list: list[float]

    Additional Attributes
    -------
    all_shared_ages = []
        merge share_ages_list (a list of lists) into a list of ages

    total_numbers_list: list[int]
        the number of children who prefer transfers by age

    total_numbers_share_list: list[int]

    priority_age_dic = {}

    priority_age_share_dic = {}
    """

    def __init__(
        self,
        d_id: int,
        recruiting_numbers_list: list[int],
        share_ages_list: list[list[int]],
        priority_child_id_list: list[int],
        priority_score_list: list[float],
    ):
        # attributes from dictionary
        self.id = d_id
        self.recruiting_numbers = recruiting_numbers_list
        self.share_ages_list = share_ages_list
        self.priority = priority_child_id_list
        self.score_list = priority_score_list
        # additional attributes
        self.all_shared_ages = [age for ages in self.share_ages_list for age in ages]
        self.total_numbers = [x for x in self.recruiting_numbers]
        self.total_numbers_share = [x for x in self.recruiting_numbers]
        self.priority_age_dic = {}
        self.priority_age_share_dic = {}

    def __str__(self):
        return f"daycare {self.id}"

    def __repr__(self):
        return f"daycare {self.id}"

    def update_priority_age_dic(self, children):
        """
        create a priority dictionary by age from self.priority_list
        """
        self.priority_age_dic = {}
        for age in range(6):
            self.priority_age_dic[age] = []
        for c_id in self.priority:
            child = next((c for c in children if c.id == c_id), None)

            if c_id not in self.priority_age_dic[child.age]:
                self.priority_age_dic[child.age].append(c_id)

    def update_priority_age_share_dic(self, children):
        """
        create a priority dictionary by age that allows for flexible quotas from self.priority_list
        """
        if self.share_ages_list is None:
            self.priority_age_share_dic = self.priority_age_dic
        else:
            self.priority_age_share_dic = {}
            for age in range(6):
                self.priority_age_share_dic[age] = []
            # traversing the children in self.priority_child_id_list once
            for c_id in self.priority:
                c = next((c for c in children if c.id == c_id), None)
                if c.age in self.all_shared_ages:
                    for ages in self.share_ages_list:
                        if (
                            c.age in ages
                        ):  # if c belongs to some group`ages` in self.share_ages_list
                            for (
                                age
                            ) in (
                                ages
                            ):  # add child to each priority_age_share_dic[age] with age in group`ages`
                                if (
                                    c.id not in self.priority_age_share_dic[age]
                                ):  # caution : use `age` instead of `c.age`
                                    self.priority_age_share_dic[age].append(c.id)
                else:
                    if c.id not in self.priority_age_share_dic[c.age]:
                        self.priority_age_share_dic[c.age].append(c.id)

    # notation \hat{G}(d, g)
    def return_related_ages(self, age):
        """
        return a list of ages belonging to the same group as the given age
        """
        if age in self.all_shared_ages:
            for ages in self.share_ages_list:
                if age in ages:
                    return ages
        else:
            ralted_ages = []
            ralted_ages.append(age)
            return ralted_ages

    # notation C_{better}(d, c, bool)
    def return_better_children_than_child_excluding_siblings(
        self, child_id, children, allow_share_bool=True, exclude_bool=True
    ):
        """
        Input:
            child_id: given child_id
            children: all children list
            allow_share_bool: bool
        Output:
            all children who
                i) have higher priority than the given child_id
                ii) have the same age / related age as the given child
                iii) are not siblings of the given child (when exclude_bool=True)
        """
        better_children_id = []
        rank_dic = (
            self.priority_age_share_dic
            if allow_share_bool is True
            else self.priority_age_dic
        )
        child = next((c for c in children if c.id == child_id), None)
        pos = rank_dic[child.age].index(
            child_id
        )  # find the position of child_id in rank_dic
        for index in range(pos):  # update better_children_id
            c = next((c for c in children if c.id == rank_dic[child.age][index]), None)
            if exclude_bool is True:
                if (
                    c.family != child.family and c.id not in better_children_id
                ):  # exclude child's siblings
                    better_children_id.append(c.id)
            else:
                if c.id not in better_children_id:  # include child's siblings
                    better_children_id.append(c.id)
        return better_children_id

    # notation C^{weak}_{better}(d, c, bool)
    def return_weak_better_children_than_child_excluding_siblings(
        self,
        child_id,
        children,
        allow_share_bool=True,
        exclude_bool=True,
        search_depth=5,
    ):
        """
        Input:
            child_id: given child_id
            children: all children list
            allow_share_bool: bool
        Output:
            all children who
                i) have no lower priority than the given child_id (almost the same scores)
                ii) have the same age / related age as the given child
                iii) are not siblings of the given child
        """
        better_children_id = []
        rank_dic = (
            self.priority_age_share_dic
            if allow_share_bool is True
            else self.priority_age_dic
        )
        child = next((c for c in children if c.id == child_id), None)
        pos = rank_dic[child.age].index(
            child_id
        )  # find the position of child_id in rank_dic
        # determine how many children with the same priority score but lower priority need to be searched
        end = min(pos + search_depth, len(rank_dic[child.age]))
        for index in range(end):
            c = next((c for c in children if c.id == rank_dic[child.age][index]), None)
            if index < pos:
                if exclude_bool is True:
                    if (
                        c.family != child.family and c.id not in better_children_id
                    ):  # exclude child's siblings
                        better_children_id.append(c.id)
                else:
                    if c.id not in better_children_id:  # include child's siblings
                        better_children_id.append(c.id)
            else:
                child_score = self.score_list[self.priority.index(child.id)]
                c_score = self.score_list[self.priority.index(c.id)]
                if exclude_bool is True:
                    if (
                        abs(c_score / child_score - 1) <= 0.00001
                        and c.id != child.id
                        and c.family != child.family
                        and c.id not in better_children_id
                    ):
                        better_children_id.append(c.id)
                else:
                    if (
                        abs(c_score / child_score - 1) <= 0.00001
                        and c.id != child.id
                        and c.id not in better_children_id
                    ):
                        better_children_id.append(c.id)

        return better_children_id


class CP_Family:
    """
    Attributes from dictionary
    ----------
    id: int

    children: list[int=Child.id]

    pref: list[tuple[int=Daycare.id]]

    Additional Attributes
    -------
    assignment: tuple[int=Daycare.id]

    has_siblings: bool
    """

    def __init__(
        self,
        f_id: int,
        children_id_list: list = [int],
        pref_list: list = [int],
        assignment_daycare_id_list=None,
    ):
        self.id = f_id
        self.children = children_id_list
        self.pref = pref_list
        self.assignment = assignment_daycare_id_list
        self.has_siblings = len(self.children) > 1

    def __str__(self):
        return f"family {self.id}"

    def __repr__(self):
        return f"family {self.id}"

    # notation D(f, p)
    def return_daycare_id_for_certain_position(self, position):
        """
        return a set of disjoint daycare_ids for the given position in family.pref
        """
        disjoint_d_ids = []
        for d_id in self.pref[position]:
            if d_id not in disjoint_d_ids:
                disjoint_d_ids.append(d_id)
        return disjoint_d_ids

    # notation C(f, p, d)
    def return_children_for_certain_position_and_daycare(self, position, daycare_id):
        """
        returns a set of siblings who apply to daycare_id at given position
        """
        children_index = []
        for index, d_id in enumerate(self.pref[position]):
            if d_id == daycare_id and index not in children_index:
                children_index.append(index)
        # convert children_index into children_id
        children_id = []
        for index in children_index:
            children_id.append(self.children[index])
        return children_id

    # notation C(f,p,d,g,bool)
    def return_siblings_for_certain_position_daycare_age(
        self, position, daycare_id, age, share_bool, children, daycares
    ):
        """
        return a set of siblings who i) apply to daycare_id at given position and ii) belong to the same age or age group
        """
        children_id_age = []
        children_id = self.return_children_for_certain_position_and_daycare(
            position, daycare_id
        )
        used_ages = []
        if share_bool is True:
            daycare = next((d for d in daycares if d.id == daycare_id), None)
            used_ages = daycare.return_related_ages(age)
        else:
            used_ages = [age]
        # update children_id_age
        if len(children_id) != 0:
            for c_id in children_id:
                child = next((c for c in children if c.id == c_id), None)
                if child.age in used_ages and child.id not in children_id_age:
                    children_id_age.append(child.id)
        return children_id_age

    # function C_{worst}(f, p, d, g, bool)
    def return_lowest_sibling_for_certain_position_daycare_age(
        self, position, daycare_id, age, share_bool, children_list, daycare_list
    ):
        """
        return the worst sibling who i) apply to daycare_id at given position and ii) belong to the same age or age group
        """
        children_id_age = self.return_siblings_for_certain_position_daycare_age(
            position, daycare_id, age, share_bool, children_list, daycare_list
        )
        daycare = next((d for d in daycare_list if d.id == daycare_id), None)
        # determine which priority_dic will be used controlled by share_bool
        rank_dic = (
            daycare.priority_age_share_dic
            if share_bool is True
            else daycare.priority_age_dic
        )
        # find the worst child_id
        worst_index = -1
        worst_child_id = -1
        for c_id in children_id_age:
            if rank_dic[age].index(c_id) > worst_index:
                worst_index = rank_dic[age].index(c_id)
                worst_child_id = c_id
        return worst_child_id
